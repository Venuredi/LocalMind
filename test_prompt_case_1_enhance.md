⚡ **Enhance Request**

## Objective
Add virtualization to AssetListGrid to handle 10,000+ rows efficiently

**Target:** `AssetListGrid.tsx`
**Context:** Full codebase analysis with dependencies

## Target Source Code

**File:** `periverse-web-application-front-end-service/apps/peri-track/src/components/AssetListGrid.tsx`
**Type:** component
**Lines:** 162

```typescript
import { Box } from '@mui/material';
import {
  DataGridPremium,
  GRID_AGGREGATION_FUNCTIONS,
} from '@mui/x-data-grid-premium';
import { AssetEntity } from '@peritasai/repository';
import { AssetType } from '@peritasai/types';
import { useMemo } from 'react';
import {
  availableCountAggregation,
  buildAssetColumns,
  buildAssetGroupingColDef,
  dataGridSx,
  DEFAULT_SORTING_ORDER,
  ErrorOverlay,
  gridContainerSx,
  gridWrapperSx,
  GRID_COLUMN_HEADER_HEIGHT,
  GRID_INITIAL_STATE,
  GRID_ROW_HEIGHT,
  NoRowsOverlay,
  PAGE_SIZE_OPTIONS,
  TableLoadingSkeleton,
  useAssetListGridState,
} from './asset-list-grid';

interface AssetListGridProps {
  typeFilter?: AssetType;
  searchQuery?: string;
  loadingOverride?: boolean;
  onLoadingChange?: (isLoading: boolean) => void;
  gridHeight?: string | number;
  onStartOver?: () => void;
  onRowClick?: (row: AssetEntity) => void;
}

export function AssetListGrid({
  typeFilter,
  searchQuery,
  loadingOverride,
  onLoadingChange,
  gridHeight,
  onStartOver,
  onRowClick,
}: AssetListGridProps) {
  const {
    error,
    hasSearchQuery,
    paginationModel,
    paginationMode,
    resolvedLoading,
    refetch,
    rowCount,
    rowGroupingModel,
    rows,
    setPaginationModel,
    setRowGroupingModel,
  } = useAssetListGridState({
    typeFilter,
    searchQuery,
    loadingOverride,
    onLoadingChange,
  });

  const handlePaginationModelChange = (newModel: typeof paginationModel) => {
    setPaginationModel({ ...newModel });
  };

  // Get columns based on type filter
  const columns = useMemo(() => buildAssetColumns(typeFilter), [typeFilter]);

  // Column visibility model - hide name column when grouping is enabled for TRAY
  const columnVisibilityModel = useMemo(() => {
    if (typeFilter === AssetType.TRAY) {
      return { name: false };
    }
    return { name: true };
  }, [typeFilter]);

  const groupingColDef = useMemo(
    () => buildAssetGroupingColDef(typeFilter),
    [typeFilter]
  );
  // Removed 'rows' from dependency array as we no longer filter rows manually
  if (error) {
    return (
      <Box sx={gridWrapperSx}>
        <Box sx={gridContainerSx(true, true, gridHeight)}>
          <ErrorOverlay
            onStartOver={onStartOver}
            onTryAgain={() => void refetch()}
          />
        </Box>
      </Box>
    );
  }

  return (
      <Box sx={gridWrapperSx}>
      <Box sx={gridContainerSx(rows.length > 0, resolvedLoading, gridHeight)}>
        <DataGridPremium
          rows={rows}
          rowHeight={GRID_ROW_HEIGHT}
          columnHeaderHeight={GRID_COLUMN_HEADER_HEIGHT}
          columns={columns}
          loading={resolvedLoading}
          disableRowSelectionOnClick
          disableColumnFilter
          disableColumnMenu
          disableColumnSelector
          disableDensitySelector
          pagination
          paginationModel={paginationModel}
          onPaginationModelChange={handlePaginationModelChange}
          pageSizeOptions={PAGE_SIZE_OPTIONS}
          {...(paginationMode === 'server' && { rowCount })}
          paginationMode={paginationMode}
          rowGroupingModel={rowGroupingModel}
          onRowGroupingModelChange={setRowGroupingModel}
          {...(typeFilter === AssetType.TRAY && { groupingColDef })}
          columnVisibilityModel={columnVisibilityModel}
          sortingOrder={DEFAULT_SORTING_ORDER}
          aggregationFunctions={{
            ...GRID_AGGREGATION_FUNCTIONS,
            availableCount: availableCountAggregation,
          }}
          initialState={GRID_INITIAL_STATE}
          getAggregationPosition={() => 'inline'}
          slots={{
            loadingOverlay: () => (
              <TableLoadingSkeleton
                columns={columns}
                columnVisibilityModel={columnVisibilityModel}
                typeFilter={typeFilter}
              />
            ),
            noRowsOverlay: () => (
              <NoRowsOverlay hasSearchQuery={hasSearchQuery} />
            ),
          }}
          slotProps={{
            basePagination: {},
          }}
          onRowClick={(params) => {
            const rowNode = (params as { rowNode?: { type?: string } })
              .rowNode;
            if (rowNode?.type === 'group') return;
            if (!params?.row) return;
            if (
              typeof (params.row as AssetEntity)
                .getLocationDisplayWithTimestamp !== 'function'
            ) {
              return;
            }
            onRowClick?.(params.row as AssetEntity);
          }}
          sx={dataGridSx(rows.length > 0, resolvedLoading)}
        />
      </Box>
    </Box>
  );
}

```

## Related Components

These components are used by or related to the target:


### Components

**rows** (`periverse-web-application-front-end-service/apps/periverse/src/features/mui-license-test/mui-license-test.tsx`) - 51 lines
```typescript
const rows = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    department: 'Engineering',
    role: 'Senior Developer',
    salary: 95000,
    startDate: new Date('2020-01-15'),
    status: 'Active',
    performance: 4.5,
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane@example.com',
    department: 'Engineering',
    role: 'Tech Lead',
    salary: 120000,
    startDate: new Date('2019-03-20'),
// ... (31 more lines)
```

**mockHandleSearchSubmit** (`periverse-web-application-front-end-service/apps/periverse/src/features/navigation/components/header/periverse-header.test.tsx`) - 51 lines
```typescript
const mockHandleSearchSubmit = jest.fn();

jest.mock('./hooks', () => ({
  useTrackAssetSearch: jest.fn(() => ({
    handleAssetTypeSelect: jest.fn(),
    handleClearSearch: jest.fn(),
    handleSearchChange: jest.fn(),
    handleSearchFocus: jest.fn(),
    handleSearchSubmit: mockHandleSearchSubmit,
    isDropdownOpen: false,
    searchValue: '',
    setIsDropdownOpen: jest.fn(),
  })),
}));

jest.mock('./periverse-header-search', () => ({
  PeriverseHeaderSearch: ({
    onSearchKeyDown,
  }: {
    onSearchKeyDown: (event: KeyboardEvent<HTMLInputElement>) => void;
// ... (31 more lines)
```

**handleResetClick** (`periverse-web-application-front-end-service/apps/peri-tray/src/app/app.tsx`) - 51 lines
```typescript
  const handleResetClick = useCallback(() => {
    setShowResetModal(true);
  }, []);

  const handleResetCancel = useCallback(() => {
    setShowResetModal(false);
  }, []);

  const handleResetConfirm = useCallback(() => {
    handleReset(() => setShowResetModal(false));
  }, [handleReset]);

  const restartConfirmationVisualVariant =
    selectedTray?.status === 'IN_ASSEMBLY' ? 'warning' : 'destructive';

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
// ... (31 more lines)
```


## Enhancement Tasks

Please enhance the code based on: **Add virtualization to AssetListGrid to handle 10,000+ rows efficiently**

Focus on:

1. **Implementation**: Add the requested enhancement cleanly and efficiently
2. **Performance**: Ensure any new code is optimized (use useMemo, useCallback where appropriate)
3. **Type Safety**: Maintain strict TypeScript typing
4. **UX**: Consider loading states, error handling, and edge cases
5. **Testing**: Suggest what should be tested
6. **Documentation**: Add JSDoc comments for complex logic

**Constraints:**
- Maintain existing coding patterns and style
- Don't break existing functionality
- Follow Material-UI and React best practices
- Keep the component composable and reusable

---
*Generated by LocalMind Code Intelligence - 2026-04-07 23:36*
*Full codebase context with 5 frontend, 0 backend, 0 data components*