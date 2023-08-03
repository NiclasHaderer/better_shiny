export const stringifyEvent = (e: Event): string => {
  const obj: Record<string, any> = {};
  for (let k in e) {
    if (k.startsWith("MOZ")) continue;
    obj[k] = (e as any)[k as any];
  }
  return JSON.stringify(
    obj,
    (_: string, v: any): string | any => {
      if (v instanceof Node) return "Node";
      if (v instanceof Window) return "Window";
      return v;
    },
    " "
  );
};
