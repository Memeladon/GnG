package handlers

import (
	"encoding/json"
	"gng/internal/auth"
	"gng/internal/models"
	"gng/internal/services"
	"gng/internal/utils/logger"
	"gng/internal/utils/responses"
	"net/http"

	"github.com/go-chi/chi/v5"
)

type AuthHandler struct {
	userService *services.UserService
	logger      *logger.Logger

	passwordHasher auth.Hasher
}

func NewAuthHandler(userService *services.UserService, logger *logger.Logger) *AuthHandler {
	return &AuthHandler{
		userService:    userService,
		logger:         logger,
		passwordHasher: auth.NewPasswordHash(),
	}
}

func (h *AuthHandler) Routes(r chi.Router) {
	r.Post("/login", h.Login)
	r.Post("/register", h.Register)
}

func (h *AuthHandler) Login(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	var userLogin models.UserLogin

	if err := json.NewDecoder(r.Body).Decode(&userLogin); err != nil {
		http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
		return
	}

	user, err := h.userService.GetByLogin(ctx, userLogin.Login)
	if err != nil {
		http.Error(w, "user does not exist", http.StatusBadRequest)
		return
	}

	if err := h.passwordHasher.Compare(user.Password, userLogin.Password); err != nil {
		http.Error(w, "wrong password", http.StatusBadRequest)
		return
	}

	// TODO: send jwt token
	responses.Simple(w, user, nil)
}

func (h *AuthHandler) Register(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	var userCreate models.UserCreate

	if err := json.NewDecoder(r.Body).Decode(&userCreate); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	passwordHash, err := h.passwordHasher.Hash(userCreate.Password)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	userCreate.Password = passwordHash

	newUser, err := h.userService.Create(ctx, userCreate)
	if err != nil {
		responses.Simple(w, nil, err)
		return
	}

	responses.Simple(w, newUser, nil)
}
