package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"github.com/joho/godotenv"

	"gng/internal/database/postgres"
	"gng/internal/handlers"
	"gng/internal/utils"
	"gng/internal/services"
)

func main() {
	// Инициализация логгера
	log := logger.NewLogger()

	if err := godotenv.Load(); err != nil {
		log.Info("No .env file found, using system environment variables")
	}

	// База данных
	db, err := postgres.NewConnection(log)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Сервисы
	userService := services.NewUserService(db.DB, log)
	gameService := services.NewGameService(db.DB, log)
	itemService := services.NewItemService(db.DB, log)

	// Обработчики
	userHandler := handlers.NewUserHandler(userService, log)
	gameHandler := handlers.NewGameHandler(gameService, log)
	itemHandler := handlers.NewItemHandler(itemService, log)

	// Роутер
	r := chi.NewRouter()

	// Мидлвары
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: true,
		MaxAge:           300,
	}))

	// Роуты
	r.Route("/api/v1", func(r chi.Router) {
		r.Route("/users", userHandler.Routes)
		r.Route("/games", gameHandler.Routes)
		r.Route("/items", itemHandler.Routes)
	})

	// Health check
	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	srv := &http.Server{
		Addr:         ":" + port,
		Handler:      r,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Горутина для запуска сервера
	go func() {
		log.Infof("Server starting on port %s", port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed to start: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info("Server shutting down...")

	// Выключение
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Info("Server exited")
}
