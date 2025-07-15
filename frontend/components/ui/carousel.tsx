"use client";

import * as React from "react";
import useEmblaCarousel, {
  type UseEmblaCarouselType,
} from "embla-carousel-react";

import { cn } from "@/lib/utils";

type CarouselApi = UseEmblaCarouselType[1];
type UseCarouselParameters = Parameters<typeof useEmblaCarousel>;
type CarouselOptions = UseCarouselParameters[0];
type CarouselPlugin = UseCarouselParameters[1];

type CarouselProps = {
  opts?: CarouselOptions;
  plugins?: CarouselPlugin;
  orientation?: "horizontal" | "vertical";
  setApi?: (api: CarouselApi) => void;
};

type CarouselContextProps = {
  carouselRef: ReturnType<typeof useEmblaCarousel>[0];
  api: ReturnType<typeof useEmblaCarousel>[1];
  scrollPrev: () => void;
  scrollNext: () => void;
  canScrollPrev: boolean;
  canScrollNext: boolean;
} & CarouselProps;

const CarouselContext = React.createContext<CarouselContextProps | null>(null);

function useCarousel() {
  const context = React.useContext(CarouselContext);

  if (!context) {
    throw new Error("useCarousel must be used within a <Carousel />");
  }

  return context;
}

function Carousel({
  orientation = "horizontal",
  opts,
  setApi,
  plugins,
  className,
  children,
  ...props
}: React.ComponentProps<"div"> & CarouselProps) {
  const [carouselRef, api] = useEmblaCarousel(
    {
      ...opts,
      axis: orientation === "horizontal" ? "x" : "y",
    },
    plugins
  );
  const [canScrollPrev, setCanScrollPrev] = React.useState(false);
  const [canScrollNext, setCanScrollNext] = React.useState(false);

  const onSelect = React.useCallback((api: CarouselApi) => {
    if (!api) return;
    setCanScrollPrev(api.canScrollPrev());
    setCanScrollNext(api.canScrollNext());
  }, []);

  const scrollPrev = React.useCallback(() => {
    api?.scrollPrev();
  }, [api]);

  const scrollNext = React.useCallback(() => {
    api?.scrollNext();
  }, [api]);

  const handleKeyDown = React.useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        scrollPrev();
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        scrollNext();
      }
    },
    [scrollPrev, scrollNext]
  );

  React.useEffect(() => {
    if (!api || !setApi) return;
    setApi(api);
  }, [api, setApi]);

  React.useEffect(() => {
    if (!api) return;
    onSelect(api);
    api.on("reInit", onSelect);
    api.on("select", onSelect);

    return () => {
      api?.off("select", onSelect);
    };
  }, [api, onSelect]);

  return (
    <CarouselContext.Provider
      value={{
        carouselRef,
        api: api,
        opts,
        orientation:
          orientation || (opts?.axis === "y" ? "vertical" : "horizontal"),
        scrollPrev,
        scrollNext,
        canScrollPrev,
        canScrollNext,
      }}
    >
      <div
        onKeyDownCapture={handleKeyDown}
        className={cn("relative", className)}
        role="region"
        aria-roledescription="carousel"
        data-slot="carousel"
        {...props}
      >
        {children}
      </div>
    </CarouselContext.Provider>
  );
}

function CarouselContent({ className, ...props }: React.ComponentProps<"div">) {
  const { carouselRef, orientation } = useCarousel();

  return (
    <div
      ref={carouselRef}
      className="overflow-hidden"
      data-slot="carousel-content"
    >
      <div
        className={cn(
          "flex",
          orientation === "horizontal" ? "-ml-4" : "-mt-4 flex-col",
          className
        )}
        {...props}
      />
    </div>
  );
}

function CarouselItem({ className, ...props }: React.ComponentProps<"div">) {
  const { orientation } = useCarousel();

  return (
    <div
      role="group"
      aria-roledescription="slide"
      data-slot="carousel-item"
      className={cn(
        "min-w-0 shrink-0 grow-0 basis-full",
        orientation === "horizontal" ? "pl-4" : "pt-4",
        className
      )}
      {...props}
    />
  );
}

// Add a tall chevron SVG component
function TallChevron({
  direction = "left",
  ...props
}: {
  direction: "left" | "right";
  className?: string;
}) {
  return (
    <svg
      width="36"
      height="194"
      viewBox="0 0 36 194"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={props.className}
      aria-hidden="true"
    >
      {direction === "left" ? (
        <polyline
          points="28,24 10,97 28,170"
          stroke="currentColor"
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
        />
      ) : (
        <polyline
          points="10,24 28,97 10,170"
          stroke="currentColor"
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
        />
      )}
    </svg>
  );
}

// Replace CarouselPrevious and CarouselNext to use the tall chevron
function CarouselPrevious({
  className,
  ...props
}: React.ComponentProps<"div"> & { className?: string }) {
  const { orientation, scrollPrev, canScrollPrev } = useCarousel();

  return (
    <div
      data-slot="carousel-previous"
      tabIndex={canScrollPrev ? 0 : -1}
      role="button"
      aria-label="Previous slide"
      onClick={canScrollPrev ? scrollPrev : undefined}
      onKeyDown={(e) => {
        if (canScrollPrev && (e.key === "Enter" || e.key === " ")) scrollPrev();
      }}
      className={cn(
        "absolute cursor-pointer select-none flex items-center justify-center",
        "transition-opacity",
        canScrollPrev ? "opacity-100" : "opacity-50 pointer-events-none",
        orientation === "horizontal"
          ? "top-1/2 -left-12 -translate-y-1/2 h-[194px]"
          : "-top-12 left-1/2 -translate-x-1/2 rotate-90 h-[194px]",
        className
      )}
      style={{ width: 48 }}
      {...props}
    >
      <TallChevron
        direction="left"
        className="stroke-gradient-hover w-9 h-[194px]"
      />
      <span className="sr-only">Previous slide</span>
    </div>
  );
}

function CarouselNext({
  className,
  ...props
}: React.ComponentProps<"div"> & { className?: string }) {
  const { orientation, scrollNext, canScrollNext } = useCarousel();

  return (
    <div
      data-slot="carousel-next"
      tabIndex={canScrollNext ? 0 : -1}
      role="button"
      aria-label="Next slide"
      onClick={canScrollNext ? scrollNext : undefined}
      onKeyDown={(e) => {
        if (canScrollNext && (e.key === "Enter" || e.key === " ")) scrollNext();
      }}
      className={cn(
        "absolute cursor-pointer select-none flex items-center justify-center",
        "transition-opacity",
        canScrollNext ? "opacity-100" : "opacity-50 pointer-events-none",
        orientation === "horizontal"
          ? "top-1/2 -right-12 -translate-y-1/2 h-[194px]"
          : "-bottom-12 left-1/2 -translate-x-1/2 rotate-90 h-[194px]",
        className
      )}
      style={{ width: 48 }}
      {...props}
    >
      <TallChevron
        direction="right"
        className="stroke-gradient-hover w-9 h-[194px]"
      />
      <span className="sr-only">Next slide</span>
    </div>
  );
}

export {
  type CarouselApi,
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
};
