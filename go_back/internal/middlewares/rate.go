package middlewares

import (
	"gng/internal/utils/helpers"
	"gng/internal/utils/helpers/types"
	"net/http"
	"strconv"
	"sync"
)

const (
	DefaultRateLimit = "1000"
)

var (
	limitChan chan types.None

	initOnce sync.Once
)

func initRateLimit() {
	l := helpers.GetEnv("RATE_LIMIT", DefaultRateLimit)
	rateLimit, err := strconv.Atoi(l)
	if err != nil || rateLimit < 0 {
		panic("env var RATE_LIMIT must be a positive integer number")
	}

	limitChan = make(chan types.None, rateLimit)
}

func RateLimit(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		initOnce.Do(initRateLimit)

		select {
		case limitChan <- types.None{}:
			next.ServeHTTP(w, r)
			<-limitChan
		default:
			http.Error(w, http.StatusText(http.StatusTooManyRequests), http.StatusTooManyRequests)
			return
		}
	})
}
