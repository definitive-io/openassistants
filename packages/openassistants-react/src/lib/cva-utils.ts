import type { StringToBoolean, ClassValue } from "class-variance-authority/dist/types";

type ConfigSchema = Record<string, Record<string, ClassValue>>;

export type ConfigVariants<T extends ConfigSchema> = {
  [Variant in keyof T]?: StringToBoolean<keyof T[Variant]> | null | undefined;
};
