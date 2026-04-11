♻️ **Refactor Request**

## Objective
Refactor useAssetListGridState hook to use React Query

**Target:** `useAssetListGridState`
**Context:** Full codebase analysis with dependencies

## Target Source Code

**File:** `periverse-web-application-front-end-service/apps/peri-track/src/components/asset-list-grid/hooks/useAssetListGridState.ts`
**Type:** hook
**Lines:** 312

```typescript
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AssetEntity, useAssetsPaginated } from '@peritasai/repository';
import { AssetType } from '@peritasai/types';
import type {
  GridFeatureMode,
  GridRowGroupingModel,
} from '@mui/x-data-grid-premium';
import { DEFAULT_PAGINATION_MODEL } from '../config';

export const useAssetListGridState = ({
  typeFilter,
  searchQuery,
  loadingOverride,
  onLoadingChange,
}: {
  typeFilter?: AssetType;
  searchQuery?: string;
  loadingOverride?: boolean;
  onLoadingChange?: (isLoading: boolean) => void;
}) => {
  const normalizedSearch = useMemo(
    () => searchQuery?.trim() ?? '',
    [searchQuery]
  );
  const searchTokens = useMemo(
    () => normalizedSearch.split(/\s+/).filter(Boolean),
    [normalizedSearch]
  );
  const isCaseIdSearch = useMemo(() => {
    if (normalizedSearch.length < 6 || normalizedSearch.length > 10) {
      return false;
    }
    if (searchTokens.length !== 1) {
      return false;
    }
    return /^[a-z0-9-]+$/i.test(normalizedSearch);
  }, [normalizedSearch, searchTokens.length]);
  const hasSearchQuery = normalizedSearch.length > 0;

  const filters = useMemo(() => {
    const filterParams: { type?: string; name?: string } = {};

    if (typeFilter) {
      filterParams.type = typeFilter;
    } else {
      filterParams.type = `${AssetType.CASE_CART},${AssetType.TRAY},${AssetType.EQUIPMENT},${AssetType.STRETCHER}`;
    }

    return filterParams;
  }, [typeFilter]);

  const [page, setPage] = useState(DEFAULT_PAGINATION_MODEL.page);
  const [pageSize, setPageSize] = useState(
    DEFAULT_PAGINATION_MODEL.pageSize
  );
  const paginationModel = useMemo(
    () => ({
      page,
      pageSize,
    }),
    [page, pageSize]
  );
  const setPaginationModel = useCallback(
    (model: typeof DEFAULT_PAGINATION_MODEL) => {
      setPage(model.page);
      setPageSize(model.pageSize);
    },
    []
  );

  useEffect(() => {
    setPage(0);
  }, [typeFilter, searchQuery]);

  const [rowGroupingModel, setRowGroupingModel] =
    useState<GridRowGroupingModel>(
      typeFilter === AssetType.TRAY ? ['name'] : []
    );

  useEffect(() => {
    if (typeFilter === AssetType.TRAY) {
      setRowGroupingModel(['name']);
    } else {
      setRowGroupingModel([]);
    }
  }, [typeFilter]);

  const searchPageSize = 100;
  const fetchPage = hasSearchQuery ? 0 : page;
  const fetchPageSize = hasSearchQuery ? searchPageSize : pageSize;
  const caseSearchFilters = useMemo(
    () =>
      isCaseIdSearch
        ? {
            ...filters,
            search: normalizedSearch,
          }
        : filters,
    [filters, isCaseIdSearch, normalizedSearch]
  );

  const caseSearchQuery = useAssetsPaginated(
    caseSearchFilters,
    0,
    searchPageSize,
    isCaseIdSearch
  );

  const hasCaseSearchResults =
    isCaseIdSearch && (caseSearchQuery.data?.total ?? 0) > 0;
  const caseSearchResolved =
    caseSearchQuery.isFetched || caseSearchQuery.isError;

  const mainQueryEnabled =
    !isCaseIdSearch || (caseSearchResolved && !hasCaseSearchResults);

  const mainQuery = useAssetsPaginated(
    filters,
    fetchPage,
    fetchPageSize,
    mainQueryEnabled
  );

  const data = hasCaseSearchResults ? caseSearchQuery.data : mainQuery.data;
  const isLoading = hasCaseSearchResults
    ? caseSearchQuery.isLoading
    : mainQuery.isLoading;
  const error = hasCaseSearchResults ? caseSearchQuery.error : mainQuery.error;
  const refetch = hasCaseSearchResults
    ? caseSearchQuery.refetch
    : mainQuery.refetch;

  const onLoadingChangeRef = useRef(onLoadingChange);

  const resolvedLoading = loadingOverride ?? isLoading;

  // Keep latest callback without retriggering loading effect on new function instances.
  useEffect(() => {
    onLoadingChangeRef.current = onLoadingChange;
  }, [onLoadingChange]);

  useEffect(() => {
    onLoadingChangeRef.current?.(resolvedLoading);
  }, [resolvedLoading]);

  const rows = useMemo<AssetEntity[]>(() => {
    const baseRows = data?.assets ?? [];
    if (!hasSearchQuery || hasCaseSearchResults) {
      return baseRows;
    }

    const normalizedSearchLower = normalizedSearch.toLowerCase();
    const tokens = searchTokens.map((token) => token.toLowerCase());
    const isShortSearch = normalizedSearchLower.length <= 2;
    const tokenizeValue = (value: string) =>
      value
        .toLowerCase()
        .split(/[^a-z0-9]+/i)
        .filter(Boolean);

    const matchesShortToken = (value: string, token: string) => {
      const parts = tokenizeValue(value);
      return parts.some((part) => part.startsWith(token));
    };

    const exactMatches = baseRows.filter((asset) => {
      const location = asset.location as
        | {
            name?: string;
            id?: string;
            departmentOrUnit?: string;
            floor?: string;
            displayLocation?: string;
          }
        | null
        | undefined;

      const locationValues = [
        location?.name,
        location?.departmentOrUnit,
        location?.floor,
        location?.displayLocation,
      ]
        .filter(Boolean)
        .map((value) => String(value).toLowerCase());

      const nameValue = asset.name ? String(asset.name).toLowerCase() : '';
      const referenceValue = asset.referenceNumber
        ? String(asset.referenceNumber).toLowerCase()
        : '';
      const descriptionValue = asset.description
        ? String(asset.description).toLowerCase()
        : '';

      if (
        nameValue === normalizedSearchLower ||
        referenceValue === normalizedSearchLower ||
        descriptionValue === normalizedSearchLower ||
        locationValues.some((value) => value === normalizedSearchLower)
      ) {
        return true;
      }

      return false;
    });

    if (exactMatches.length > 0) {
      return exactMatches;
    }

    return baseRows.filter((asset) => {
      const location = asset.location as
        | {
            name?: string;
            id?: string;
            departmentOrUnit?: string;
            floor?: string;
            displayLocation?: string;
          }
        | null
        | undefined;

      const locationValues = [
        location?.name,
        location?.departmentOrUnit,
        location?.floor,
        location?.displayLocation,
      ]
        .filter(Boolean)
        .map((value) => String(value).toLowerCase());

      const nameValue = asset.name ? String(asset.name).toLowerCase() : '';
      const referenceValue = asset.referenceNumber
        ? String(asset.referenceNumber).toLowerCase()
        : '';
      const descriptionValue = asset.description
        ? String(asset.description).toLowerCase()
        : '';

      const searchableFields = [
        nameValue,
        referenceValue,
        descriptionValue,
        ...locationValues,
      ].filter(Boolean);

      // Short searches (<=2 chars) only match IDs/reference numbers and must match word starts.
      const shortSearchFields = [nameValue, referenceValue].filter(Boolean);
      const valuesForMatching = isShortSearch
        ? shortSearchFields
        : searchableFields;

      const fullText = valuesForMatching.join(' ');

      if (normalizedSearchLower.includes(' ')) {
        if (fullText.includes(normalizedSearchLower)) {
          return true;
        }

        return valuesForMatching.some((value) =>
          tokens.every((token) => value.includes(token))
        );
      }

      if (isShortSearch) {
        return tokens.every((token) =>
          valuesForMatching.some((value) => matchesShortToken(value, token))
        );
      }

      return tokens.every((token) =>
        valuesForMatching.some((value) => value.includes(token))
      );
    });
  }, [
    data?.assets,
    hasCaseSearchResults,
    hasSearchQuery,
    normalizedSearch,
    searchTokens,
  ]);

  const [rowCountState, setRowCountState] = useState(0);

  useEffect(() => {
    if (!hasSearchQuery && typeof data?.total === 'number') {
      setRowCountState(data.total);
    }
  }, [data?.total, hasSearchQuery]);

  const rowCount = hasSearchQuery ? rows.length : rowCountState;

  const paginationMode: GridFeatureMode = hasSearchQuery
    ? 'client'
    : 'server';

  return {
    data,
    error,
    filters,
    hasSearchQuery: Boolean(normalizedSearch.length > 0),
    paginationModel,
    paginationMode,
    resolvedLoading,
    refetch,
    rowCount,
    rowGroupingModel,
    rows,
    setPaginationModel,
    setRowGroupingModel,
  };
};

```

## Related Components

These components are used by or related to the target:


### Hooks

**useInstrumentDetection** (`periverse-web-application-front-end-service/apps/peri-tray/src/features/instrument-detection/hooks/use-instrument-detection.ts`) - 51 lines
```typescript
export function useInstrumentDetection(
  isActive: boolean,
  initialInstruments: Instrument[],
  sessionKey: string,
  containerWidth: number = DETECTION_DEFAULTS.CONTAINER_WIDTH,
  configOverrides?: Partial<DetectionConfig>,
  onPersistIncrement?: (catalogItemId: string) => void,
  sourceIndex?: number,
  inputMode: 'video' | 'camera' = 'video'
): UseInstrumentLifecycleResult {
  const config = useMemo(
    () => getDetectionConfig({ containerWidth, ...configOverrides }),
    [containerWidth, configOverrides]
  );
  const orchestratorRef = useRef<InstrumentOrchestrator | null>(null);
  const onPersistIncrementRef = useRef(onPersistIncrement);
  onPersistIncrementRef.current = onPersistIncrement;

  // 1. Stable hash: catalog structure only (catalogItemId + required). Sorted so API
  // response order doesn't trigger orchestrator recreation when only counts change.
// ... (31 more lines)
```

**useTrayAssembly** (`periverse-web-application-front-end-service/apps/peri-tray/src/features/tray-assembly/hooks/use-tray-assembly.ts`) - 51 lines
```typescript
export function useTrayAssembly() {
  const queryClient = useQueryClient();

  // State
  const [buildModeView, setBuildModeView] = useState<BuildModeView>('search');
  const [selectedTray, setSelectedTray] = useState<Tray | null>(null);
  const [currentAssembly, setCurrentAssembly] =
    useState<TrayAssemblyChecklist | null>(null);
  const [error, setError] = useState<AssemblyError | null>(null);
  const [lastClosedTrayId, setLastClosedTrayId] = useState<string | null>(null);
  const selectedTrayIdRef = useRef<string | null>(null);
  selectedTrayIdRef.current = selectedTray?.id ?? null;

  const buildModeViewRef = useRef<BuildModeView>(buildModeView);
  buildModeViewRef.current = buildModeView;

  const ignoreNextPopstateRef = useRef(false);

  const closeBuildView = useCallback(() => {
    const trayIdToRefresh = selectedTrayIdRef.current;
// ... (31 more lines)
```

**useRouteTitle** (`periverse-web-application-front-end-service/apps/periverse/src/shared/hooks/use-route-title.ts`) - 16 lines
```typescript
export const useRouteTitle = () => {
  const currentMatch = useRouterState({
    select: (state) => state.matches[state.matches.length - 1],
  });
  const { t } = useTranslation(['periverse']);

  const title = currentMatch?.staticData?.title;

  // If title is a translation key (contains dots), translate it
  if (title && title.includes('.')) {
    return t(title, title); // Use the key as fallback
  }

  // Otherwise return the title as-is (fallback for non-translation keys)
  return title || t('pages.caseSchedule.title', 'Case Schedule');
};

```


## Refactoring Tasks

Please refactor the code for:

1. **Clarity**: Improve code readability and maintainability
2. **Performance**: Optimize for better performance
3. **Modularity**: Extract reusable logic into hooks or utilities
4. **Type Safety**: Strengthen TypeScript types
5. **Best Practices**: Apply modern React patterns (hooks, composition)

**Constraints:**
- Maintain the same external API and behavior
- Don't introduce breaking changes
- Keep test compatibility

---
*Generated by LocalMind Code Intelligence - 2026-04-07 23:36*
*Full codebase context with 5 frontend, 0 backend, 0 data components*