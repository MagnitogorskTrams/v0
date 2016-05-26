package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/extrame/xls"
)

const baseURL = "http://www.maggortrans.ru/raspisanie/"

type output struct {
	stopID        int
	stopName      string
	stopDirection string
	route         string
	workday       bool
	timeSecs      int64
}

func main() {
	filesList, err := listFiles()
	if err != nil {
		log.Fatalln(err)
	}

	for _, URL := range filesList {
		content, err := downloadFile(URL)
		if err != nil {
			log.Fatalln(err)
		}
		recs, err := parseFile(content)
		if err != nil {
			log.Fatalln(err)
		}
		for _, rec := range recs {
			fmt.Printf("%#v\n", rec)
		}
	}
}

func listFiles() ([]string, error) {
	resp, err := http.Get(baseURL)
	if err != nil {
		return []string{}, err
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return []string{}, err
	}
	resp.Body.Close()

	re := regexp.MustCompile("[[:word:]]+.xls")
	filesNames := re.FindAllString(string(body), -1)

	filesMap := make(map[string]bool)
	for _, file := range filesNames {
		filesMap[file] = true
	}
	filesNames = []string{}
	for key := range filesMap {
		filesNames = append(filesNames, baseURL+key)
	}

	return filesNames, nil
}

func downloadFile(URL string) ([]byte, error) {
	resp, err := http.Get(URL)
	if err != nil {
		return []byte{}, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return []byte{}, err
	}

	return body, nil
}

func parseFile(content []byte) ([]output, error) {
	wb, err := xls.OpenReader(ioutil.NopCloser(bytes.NewReader(content)), "utf-8")
	if err != nil {
		log.Fatal(err)
	}

	result := []output{}
	for i := 0; i < wb.NumSheets(); i++ {
		sheet := wb.GetSheet(i)

		if sheet.MaxRow != 0 {
			//костыли-костылики
			if sheet.Name == "Черняховского" {
				continue
			}

			cells := make([][]string, int(sheet.MaxRow)+1)
			//magic
			for k, row := range sheet.Rows {
				var data []string
				if len(row.Cols) > 0 {
					for _, col := range row.Cols {
						if uint16(len(data)) <= col.LastCol() {
							data = append(data, make([]string, col.LastCol()-uint16(len(data))+1)...)
						}
						str := col.String(wb)
						for i := uint16(0); i < col.LastCol()-col.FirstCol()+1; i++ {
							data[col.FirstCol()+i] = str[i]
						}
					}
					cells[k] = data
				}
			}
			cells = filterSheet(cells)

			var lastFilled int
			//concat rows of the same route
			for idx, row := range cells {
				if row[0] == "" {
					cells[lastFilled] = append(cells[lastFilled], row[1:]...)
					cells[idx] = []string{}
				} else {
					lastFilled = idx
				}
			}
			cells = filterSheet(cells)

			//trying get stop id from sheet name
			stopID, err := strconv.Atoi(strings.Split(sheet.Name, " ")[0])
			if err != nil {
				log.Fatal(err, sheet.Name)
			}
			if sheet.Name == "50 лет Маг" {
				stopID = 4
			}

			sp := strings.Split(cells[0][0], "\"")
			stopName := sp[1]
			var ns []string
			for k := 3; k < len(sp); k += 2 {
				ns = append(ns, sp[k])
			}
			stopDirection := strings.Join(ns, ";")

			workday := true
			for i := 3; i < len(cells); i++ {
				if cells[i][0] == "Выходные дни" {
					workday = false
					i++
					continue
				}

				for j := 1; j < len(cells[i]); j++ {
					f, _ := strconv.ParseFloat(cells[i][j], 64)
					out := output{
						stopID:        stopID,
						stopName:      stopName,
						stopDirection: stopDirection,
						workday:       workday,
						route:         cells[i][0],
						timeSecs:      int64(f * 60 * 60 * 24),
					}
					result = append(result, out)
				}
			}
		}
	}

	return result, nil
}

func filterSheet(sheet [][]string) [][]string {
	var res [][]string
	for _, row := range sheet {
		row = filterRow(row)
		if len(row) > 0 {
			res = append(res, row)
		}
	}

	return res
}

func filterRow(row []string) []string {
	var lastFilled int
	for idx, cell := range row {
		if len(cell) > 0 {
			lastFilled = idx + 1
		}
	}

	return row[:lastFilled]
}
