export default function SkeletonCard() {
  return (
    <div className="flex-shrink-0 w-44 animate-pulse">
      <div className="rounded-lg aspect-[2/3] bg-[#161616]" />
      <div className="mt-2.5 space-y-1.5">
        <div className="h-3 bg-[#161616] rounded w-3/4" />
        <div className="h-2.5 bg-[#161616] rounded w-1/2" />
      </div>
    </div>
  );
}
