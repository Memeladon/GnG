package password

import (
	"fmt"

	"golang.org/x/crypto/bcrypt"
)

const (
	MaxPasswordSize = 32
)

type Hasher interface {
	Hash(string) (string, error)
	Compare(hash string, str string) error
}

type BcryptHasher struct {
	cost int
}

func NewBcryptHasher() *BcryptHasher {
	return &BcryptHasher{
		cost: bcrypt.MinCost,
	}
}

func (h *BcryptHasher) Hash(str string) (string, error) {
	if str == "" || len(str) > MaxPasswordSize {
		return "", fmt.Errorf("password %s is incompatible for hashing", str)
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(str), h.cost)
	if err != nil {
		return "", err
	}

	return string(hash), nil
}

func (h *BcryptHasher) Compare(hash string, str string) error {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(str))
}
