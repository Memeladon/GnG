package handlers

import (
	"net/http"

	"gng/internal/services"
	"gng/internal/utils/logger"

	"github.com/go-chi/chi/v5"
)

type UserHandler struct {
	userService *services.UserService
	logger      *logger.Logger
}

func NewUserHandler(userService *services.UserService, logger *logger.Logger) *UserHandler {
	return &UserHandler{
		userService: userService,
		logger:      logger,
	}
}

func (h *UserHandler) Routes(r chi.Router) {
	r.Get("/", h.List)
	r.Get("/{id}", h.GetByID)
	r.Put("/{id}", h.Update)
	r.Delete("/{id}", h.Delete)
}

func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("List users - not implemented yet"))
}

func (h *UserHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Get user by ID - not implemented yet"))
}

func (h *UserHandler) Update(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Update user - not implemented yet"))
}

func (h *UserHandler) Delete(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Delete user - not implemented yet"))
}
