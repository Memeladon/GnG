package handlers

import (
	"net/http"

	"gng/internal/services"

	"github.com/go-chi/chi/v5"
)

// GameHandler обрабатывает HTTP-запросы, связанные с играми
type GameHandler struct {
	gameService *services.GameService
}

// NewGameHandler создает новый обработчик игр
func NewGameHandler(gameService *services.GameService) *GameHandler {
	return &GameHandler{
		gameService: gameService,
	}
}

// Routes настраивает маршруты для игровых эндпоинтов
func (h *GameHandler) Routes(r chi.Router) {
	r.Get("/", h.List)
	r.Post("/", h.Create)
	r.Get("/{id}", h.GetByID)
	r.Put("/{id}", h.Update)
	r.Delete("/{id}", h.Delete)
}

// List обрабатывает GET /api/v1/games
func (h *GameHandler) List(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("List games - not implemented yet"))
}

// Create обрабатывает POST /api/v1/games
func (h *GameHandler) Create(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Create game - not implemented yet"))
}

// GetByID обрабатывает GET /api/v1/games/{id}
func (h *GameHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Get game by ID - not implemented yet"))
}

// Update обрабатывает PUT /api/v1/games/{id}
func (h *GameHandler) Update(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Update game - not implemented yet"))
}

// Delete обрабатывает DELETE /api/v1/games/{id}
func (h *GameHandler) Delete(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Delete game - not implemented yet"))
}
