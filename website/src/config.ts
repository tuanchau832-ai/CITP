function getApplicationUrl(value: string | undefined) {
  if (!value?.trim()) return undefined;
  try {
    const url = new URL(value.trim());
    const allowed = url.protocol === 'https:' || (import.meta.env.DEV
      && url.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname));
    if (allowed && !url.username && !url.password) return url.href;
  } catch {
    // An unfinished configuration leaves the launch control unavailable.
  }
  return undefined;
}

export const applicationUrl = getApplicationUrl(import.meta.env.VITE_HANOI_WATER_WATCH_URL);
