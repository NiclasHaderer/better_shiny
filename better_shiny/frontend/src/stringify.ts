export const stringifyEvent = (e: Event): string => {

    const obj: Record<string, any> = {};

    // Check if the event is an input, change event, or anything connected to an input
    if(e.target && "value" in e.target){
        obj["value"] = (e.target as HTMLInputElement).value;
    }


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
