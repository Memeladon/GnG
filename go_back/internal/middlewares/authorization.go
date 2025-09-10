package middlewares

import (
	"gng/internal/auth/token"
	"gng/internal/utils/helpers"
	"net/http"
	"strings"
)

type authCtxKey string

const (
	UserIDKey    authCtxKey = "userId"
	UserLoginKey authCtxKey = "userLogin"
)

const (
	tokenPrefix = "Bearer "
	authHeader  = "Authorization"
)

func AuthRoute(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ctx := r.Context()

		authToken := r.Header.Get(authHeader)
		if !strings.HasPrefix(authToken, tokenPrefix) {
			http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
			return
		}

		authToken = authToken[len(tokenPrefix):]
		claims, err := token.Parse(authToken)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
			return
		}

		ctxMap := helpers.ContextMap{
			UserIDKey:    claims.UserId,
			UserLoginKey: claims.UserLogin,
		}
		ctx = ctxMap.AddTo(ctx)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
