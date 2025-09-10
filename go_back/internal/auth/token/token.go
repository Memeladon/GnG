package token

import (
	"errors"
	"gng/internal/utils/helpers"
	"os"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

const (
	DefaultTokenLifetime = "3600s"
)

type TokenClaims struct {
	UserId    string
	UserLogin string
}

func getJwtSecret() (string, error) {
	secret := os.Getenv("JWT_SECRET")
	if secret == "" {
		return "", errors.New("jwt secret is not set")
	}

	return secret, nil
}

func newClaims(tokenClaims TokenClaims) (jwt.MapClaims, error) {
	tokenLifetimeStr := helpers.GetEnv("JWT_EXPIRY", DefaultTokenLifetime)
	tokenLifetime, err := time.ParseDuration(tokenLifetimeStr)
	if err != nil {
		return nil, errors.New("could not parse time for token creation")
	}

	expAt := time.Now().Add(tokenLifetime)

	claims := jwt.MapClaims{
		"sub":    tokenClaims.UserId,
		"subLog": tokenClaims.UserLogin,
		"exp":    expAt.Unix(), // Short expiration
	}

	return claims, nil
}

func New(tokenClaims TokenClaims) (string, error) {
	secret, err := getJwtSecret()
	if err != nil {
		return "", err
	}

	claims, err := newClaims(tokenClaims)
	if err != nil {
		return "", err
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signedToken, err := token.SignedString([]byte(secret))
	if err != nil {
		return "", errors.New("could not sign token")
	}

	return signedToken, nil
}

func Parse(signedToken string) (*TokenClaims, error) {
	secret, err := getJwtSecret()
	if err != nil {
		return nil, err
	}

	token, err := jwt.Parse(signedToken, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("unexpected signing method")
		}
		return []byte(secret), nil
	})
	if err != nil || !token.Valid {
		return nil, errors.New("invalid token")
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, errors.New("invalid token")
	}

	return &TokenClaims{
		UserId:    claims["sub"].(string),
		UserLogin: claims["subLog"].(string),
	}, nil
}
