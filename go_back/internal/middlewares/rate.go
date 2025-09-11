package middlewares

import (
	"gng/internal/utils/helpers"
	"net/http"
	"strconv"
	"sync"
)

const (
	DefaultRateLimit = "1000"
)

var (
	limitChan chan helpers.None

	rateLimit = 0
	initOnce  sync.Once
)

func initRateLimit() {
	l := helpers.GetEnv("RATE_LIMIT", DefaultRateLimit)
	rlim, err := strconv.Atoi(l)
	if err != nil || rlim < 0 {
		panic("env var RATE_LIMIT must be a positive integer number")
	}

	rateLimit = rlim
	limitChan = make(chan helpers.None, rateLimit)
}

func RateLimit(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		initOnce.Do(initRateLimit)

		select {
		case limitChan <- helpers.None{}:
			next.ServeHTTP(w, r)
			<-limitChan
		default:
			http.Error(w, http.StatusText(http.StatusTooManyRequests), http.StatusTooManyRequests)
			return
		}
	})
}
