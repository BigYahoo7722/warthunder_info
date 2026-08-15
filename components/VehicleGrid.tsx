"use client";

import { forwardRef } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { VirtuosoGrid, type GridComponents } from "react-virtuoso";
import { VehicleCard } from "./VehicleCard";
import type { Category, Nation, Vehicle, VehiclePage } from "@/lib/types";
import { CATEGORY_LABELS, NATION_LABELS } from "@/lib/types";

async function fetchVehiclePage(
  nation: Nation,
  category: Category,
  cursor: number
): Promise<VehiclePage> {
  const res = await fetch(
    `/api/vehicles?nation=${nation}&category=${category}&cursor=${cursor}`
  );
  if (!res.ok) throw new Error(`Archive request failed: ${res.status}`);
  return res.json();
}

const GridList: GridComponents["List"] = forwardRef(function GridList(
  { style, children, ...props },
  ref
) {
  return (
    <div
      ref={ref as React.Ref<HTMLDivElement>}
      style={style}
      {...props}
      className="grid grid-cols-2 gap-2.5 p-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6"
    >
      {children}
    </div>
  );
});

const GridItem: GridComponents["Item"] = ({ children, ...props }) => (
  <div {...props}>{children}</div>
);

export function VehicleGrid({
  nation,
  category,
  onOpenVehicle,
}: {
  nation: Nation;
  category: Category;
  onOpenVehicle: (v: Vehicle) => void;
}) {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
  } = useInfiniteQuery({
    queryKey: ["vehicles", nation, category],
    queryFn: ({ pageParam }) => fetchVehiclePage(nation, category, pageParam),
    getNextPageParam: (last) => last.nextCursor ?? undefined,
    initialPageParam: 0,
  });

  const items = data?.pages.flatMap((p) => p.items) ?? [];
  const total = data?.pages[0]?.total ?? 0;

  if (isError) {
    return (
      <div className="p-8 text-center">
        <p className="font-mono text-xs uppercase tracking-widest2 text-redact">
          Archive request failed
        </p>
        <p className="mt-1 font-body text-sm text-parchment/60">
          The API route couldn&apos;t be reached. Check that the dev server is running.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-2.5 p-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className="h-40 animate-pulse rounded-sm border border-hairline bg-panel"
          />
        ))}
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between border-b border-hairline px-4 py-2.5">
        <p className="font-mono text-[11px] uppercase tracking-widest2 text-parchment/50">
          {NATION_LABELS[nation]} · {CATEGORY_LABELS[category]}
        </p>
        <p className="font-mono text-[11px] text-brass">
          {items.length} / {total} loaded
        </p>
      </div>

      {items.length === 0 ? (
        <div className="p-10 text-center">
          <p className="font-display text-lg tracking-wide text-parchment/70">
            No records filed under this heading.
          </p>
        </div>
      ) : (
        <VirtuosoGrid
          useWindowScroll
          totalCount={items.length}
          components={{ List: GridList, Item: GridItem }}
          itemContent={(i) => (
            <VehicleCard vehicle={items[i]} onOpen={onOpenVehicle} />
          )}
          endReached={() => {
            if (hasNextPage && !isFetchingNextPage) fetchNextPage();
          }}
          overscan={600}
        />
      )}

      {isFetchingNextPage && (
        <p className="p-4 text-center font-mono text-[11px] uppercase tracking-widest2 text-parchment/40">
          Pulling next chunk from archive…
        </p>
      )}
    </div>
  );
}
