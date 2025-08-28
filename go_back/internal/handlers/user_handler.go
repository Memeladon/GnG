package handlers

import (
	"net/http"

	"gng/internal/utils"
	"gng/internal/services"

	"github.com/go-chi/chi/v5"
)

// UserHandler обрабатывает HTTP-запросы, связанные с пользователями
type UserHandler struct {
	userService *services.UserService
	logger      *logger.Logger
}

// NewUserHandler создает новый обработчик пользователей
func NewUserHandler(userService *services.UserService, logger *logger.Logger) *UserHandler {
	return &UserHandler{
		userService: userService,
		logger:      logger,
	}
}

// Routes настраивает маршруты для пользовательских эндпоинтов
func (h *UserHandler) Routes(r chi.Router) {
	r.Get("/", h.List)
	r.Post("/", h.Create)
	r.Get("/{id}", h.GetByID)
	r.Put("/{id}", h.Update)
	r.Delete("/{id}", h.Delete)
}

// List обрабатывает GET /api/v1/users
func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("List users - not implemented yet"))
}

// Create обрабатывает POST /api/v1/users
func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Create user - not implemented yet"))
}

// GetByID обрабатывает GET /api/v1/users/{id}
func (h *UserHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Get user by ID - not implemented yet"))
}

// Update обрабатывает PUT /api/v1/users/{id}
func (h *UserHandler) Update(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Update user - not implemented yet"))
}

// Delete обрабатывает DELETE /api/v1/users/{id}
func (h *UserHandler) Delete(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Delete user - not implemented yet"))
}
