package handlers

import (
	"encoding/json"
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
}

func NewAuthHandler(userService *services.UserService, logger *logger.Logger) *AuthHandler {
	return &AuthHandler{
		userService: userService,
		logger:      logger,
	}
}

func (h *AuthHandler) Routes(r chi.Router) {
	r.Post("/login", h.Login)
	r.Post("/register", h.Register)
}

func (h *AuthHandler) Login(w http.ResponseWriter, r *http.Request) {

}

func (h *AuthHandler) Register(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	var userCreate models.UserCreate

	if err := json.NewDecoder(r.Body).Decode(&userCreate); err != nil {
		http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
		return
	}

	// TODO: bcrypt the password

	newUser, err := h.userService.Create(ctx, userCreate)
	if err != nil {
		responses.Simple(w, nil, err)
		return
	}

	responses.Simple(w, newUser, nil)
}
