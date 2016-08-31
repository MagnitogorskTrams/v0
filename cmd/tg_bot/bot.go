package main

import (
	"database/sql"
	"flag"
	"fmt"
	"log"
	"strconv"
	"strings"

	_ "github.com/lib/pq"

	"github.com/bot-api/telegram"
	"github.com/bot-api/telegram/telebot"
	"golang.org/x/net/context"
)

var (
	token *string
	dbURL *string
	debug *bool
)

func init() {
	token = flag.String("token", "", "telegram bot token")
	dbURL = flag.String("db", "", "database URL")
	debug = flag.Bool("debug", false, "show debug information")
	flag.Parse()
}

func main() {
	if *token == "" {
		log.Fatal("token flag required")
	}

	if *dbURL == "" {
		log.Fatal("database URL flag required")
	}

	db, err := sql.Open("postgres", *dbURL)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	api := telegram.New(*token)
	api.Debug(*debug)
	bot := telebot.NewWithAPI(api)
	bot.Use(telebot.Recover())

	netCtx, cancel := context.WithCancel(context.Background())
	defer cancel()

	bot.HandleFunc(func(ctx context.Context) error {
		update := telebot.GetUpdate(ctx)
		if update.Message != nil {
			if update.Message.Location != nil {
				rows, err := db.Query(queryNear, update.Message.Location.Longitude, update.Message.Location.Latitude)
				if err != nil {
					return err
				}
				defer rows.Close()
				var ans string
				for rows.Next() {
					var id int64
					var name, direction, routes string
					if err := rows.Scan(&id, &name, &direction, &routes); err != nil {
						return err
					}
					ans += fmt.Sprintf("*%s*>%s\n%s\n/schedule\\_%d\n\n", name, direction, routes, id)

				}
				api := telebot.GetAPI(ctx)
				msg := telegram.MessageCfg{
					BaseMessage: telegram.BaseMessage{
						BaseChat:         telegram.BaseChat{ID: update.Message.Chat.ID},
						ReplyToMessageID: update.Message.MessageID,
					},
					ParseMode: telegram.MarkdownMode,
					Text:      ans,
				}
				_, err = api.SendMessage(ctx, msg)
				return err
			}
			if update.Message.IsCommand() {
				cmd, _ := update.Message.Command()
				if strings.HasPrefix(cmd, "schedule_") {
					idstr := strings.TrimPrefix(cmd, "schedule_")
					id, _ := strconv.ParseInt(idstr, 10, 64)
					rows, err := db.Query(querySchedule, id)
					if err != nil {
						return err
					}
					defer rows.Close()
					var ans, time, route string
					rows.Next()
					if err := rows.Scan(&time, &route); err != nil {
						return err
					}
					ans += fmt.Sprintf("*%s*>%s\n\n", time, route)
					for rows.Next() {
						if err := rows.Scan(&time, &route); err != nil {
							return err
						}
						ans += fmt.Sprintf("%s - *%s*\n", time, route)

					}
					api := telebot.GetAPI(ctx)
					msg := telegram.MessageCfg{
						BaseMessage: telegram.BaseMessage{
							BaseChat:         telegram.BaseChat{ID: update.Message.Chat.ID},
							ReplyToMessageID: update.Message.MessageID,
						},
						ParseMode: telegram.MarkdownMode,
						Text:      ans,
					}
					_, err = api.SendMessage(ctx, msg)
					return err
				}
				if strings.HasPrefix(cmd, "help") {
					ans += helpAns
					
					api := telebot.GetAPI(ctx)
					msg := telegram.MessageCfg{
						BaseMessage: telegram.BaseMessage{
							BaseChat:         telegram.BaseChat{ID: update.Message.Chat.ID},
							ReplyToMessageID: update.Message.MessageID,
						},
						ParseMode: telegram.MarkdownMode,
						Text:      ans,
					}
					_, err = api.SendMessage(ctx, msg)
					return err
				}
			}
		}
		return nil
	})

	err = bot.Serve(netCtx)
	if err != nil {
		log.Println(err)
		main()
	}
}

var queryNear = `select 
s.id,
s.name,
s.direction,
s.routes
from import_mgt.stops as s
order by s.geometry <-> ST_SetSRID(ST_Point($1, $2),4326)
limit 6;`

var querySchedule = `(SELECT name, direction
FROM import_mgt.stops
where id = $1)

union all

(SELECT time_str, route_str
FROM import_mgt.schedules
WHERE
time between '1970-01-01'::date + localtime + '-00:05:00' and '1970-01-01'::date + localtime + '01:00:00'
and workday = (extract(DOW from now()) not in (0, 6))
and stop_id = $1
ORDER BY schedules.time);`

var helpAns = `Ура МГТ!`
