package handlers

import (
	"net/http"

	"gng/internal/services"
	"gng/internal/utils/logger"

	"github.com/go-chi/chi/v5"
)

// ItemHandler обрабатывает HTTP-запросы, связанные с предметами
type ItemHandler struct {
	itemService *services.ItemService
	logger      *logger.Logger
}

// NewItemHandler создает новый обработчик предметов
func NewItemHandler(itemService *services.ItemService, logger *logger.Logger) *ItemHandler {
	return &ItemHandler{
		itemService: itemService,
		logger:      logger,
	}
}

// Routes настраивает маршруты для эндпоинтов предметов
func (h *ItemHandler) Routes(r chi.Router) {
	r.Get("/", h.List)
	r.Post("/", h.Create)
	r.Get("/{id}", h.GetByID)
	r.Put("/{id}", h.Update)
	r.Delete("/{id}", h.Delete)
}

// List обрабатывает GET /api/v1/items
func (h *ItemHandler) List(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("List items - not implemented yet"))
}

// Create обрабатывает POST /api/v1/items
func (h *ItemHandler) Create(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Create item - not implemented yet"))
}

// GetByID обрабатывает GET /api/v1/items/{id}
func (h *ItemHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Get item by ID - not implemented yet"))
}

// Update обрабатывает PUT /api/v1/items/{id}
func (h *ItemHandler) Update(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Update item - not implemented yet"))
}

// Delete обрабатывает DELETE /api/v1/items/{id}
func (h *ItemHandler) Delete(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Delete item - not implemented yet"))
}
