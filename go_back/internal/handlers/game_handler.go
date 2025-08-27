package handlers

import (
	"net/http"

	"github.com/go-chi/chi/v5"
)

// GameHandler handles game-related HTTP requests
type GameHandler struct {
	// gameService *services.GameService
}

// NewGameHandler creates a new game handler
func NewGameHandler(gameService interface{}) *GameHandler {
	return &GameHandler{
		// gameService: gameService,
	}
}

// Routes sets up the routes for game endpoints
func (h *GameHandler) Routes(r chi.Router) {
	r.Get("/", h.List)
	r.Post("/", h.Create)
	r.Get("/{id}", h.GetByID)
	r.Put("/{id}", h.Update)
	r.Delete("/{id}", h.Delete)
}

// List handles GET /api/v1/games
func (h *GameHandler) List(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("List games - not implemented yet"))
}

// Create handles POST /api/v1/games
func (h *GameHandler) Create(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Create game - not implemented yet"))
}

// GetByID handles GET /api/v1/games/{id}
func (h *GameHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Get game by ID - not implemented yet"))
}

// Update handles PUT /api/v1/games/{id}
func (h *GameHandler) Update(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Update game - not implemented yet"))
}

// Delete handles DELETE /api/v1/games/{id}
func (h *GameHandler) Delete(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Delete game - not implemented yet"))
}
