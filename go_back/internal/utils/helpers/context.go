package helpers

import "context"

type ContextMap map[any]any

func (cm *ContextMap) AddTo(parent context.Context) context.Context {
	ctx := parent
	for k, v := range map[any]any(*cm) {
		ctx = context.WithValue(ctx, k, v)
	}

	return ctx
}

func (cm *ContextMap) New() context.Context {
	ctx := context.Background()
	return cm.AddTo(ctx)
}
