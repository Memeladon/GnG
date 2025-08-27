package handlers

import (
	"net/http"

	"github.com/go-chi/chi/v5"
)

// ItemHandler handles item-related HTTP requests
type ItemHandler struct {
	// itemService *services.ItemService
}

// NewItemHandler creates a new item handler
func NewItemHandler(itemService interface{}) *ItemHandler {
	return &ItemHandler{
		// itemService: itemService,
	}
}

// Routes sets up the routes for item endpoints
func (h *ItemHandler) Routes(r chi.Router) {
	r.Get("/", h.List)
	r.Post("/", h.Create)
	r.Get("/{id}", h.GetByID)
	r.Put("/{id}", h.Update)
	r.Delete("/{id}", h.Delete)
}

// List handles GET /api/v1/items
func (h *ItemHandler) List(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("List items - not implemented yet"))
}

// Create handles POST /api/v1/items
func (h *ItemHandler) Create(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Create item - not implemented yet"))
}

// GetByID handles GET /api/v1/items/{id}
func (h *ItemHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Get item by ID - not implemented yet"))
}

// Update handles PUT /api/v1/items/{id}
func (h *ItemHandler) Update(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Update item - not implemented yet"))
}

// Delete handles DELETE /api/v1/items/{id}
func (h *ItemHandler) Delete(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Delete item - not implemented yet"))
}
