// Audio engine related types

// (현재 audioEngine.ts에는 별도의 타입 선언이 많지 않으나, 추후 확장성을 위해 분리)

export type PlayheadUpdateCallback = (flicks: number) => void;
