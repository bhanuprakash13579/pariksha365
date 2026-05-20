export const CATEGORY_ASSETS: Record<string, { colors: readonly [string, string, ...string[]]; iconFamily: 'Ionicons' | 'MaterialCommunityIcons'; iconName: string; iconColor: string }> = {
    // ── DB-seeded category names (must match exactly what the backend seeds) ──
    'Bank': { colors: ['#fef08a', '#fde047'], iconFamily: 'MaterialCommunityIcons', iconName: 'bank-outline', iconColor: '#854d0e' },
    'Judicial': { colors: ['#e0c3fc', '#c4b5fd'], iconFamily: 'Ionicons', iconName: 'hammer-outline', iconColor: '#5b21b6' },
    'ESIC': { colors: ['#d1fae5', '#6ee7b7'], iconFamily: 'Ionicons', iconName: 'medkit-outline', iconColor: '#065f46' },
    'Railway': { colors: ['#dcfce7', '#86efac'], iconFamily: 'Ionicons', iconName: 'train-outline', iconColor: '#166534' },
    'Defence': { colors: ['#d1fae5', '#a7f3d0'], iconFamily: 'MaterialCommunityIcons', iconName: 'shield-star', iconColor: '#065f46' },
    'PSUs': { colors: ['#f3e8ff', '#d8b4fe'], iconFamily: 'Ionicons', iconName: 'business-outline', iconColor: '#6b21a8' },
    'UPSC': { colors: ['#e0c3fc', '#8ec5fc'], iconFamily: 'MaterialCommunityIcons', iconName: 'bank', iconColor: '#4c1d95' },
    'SSC': { colors: ['#ffecd2', '#fcb69f'], iconFamily: 'Ionicons', iconName: 'briefcase-outline', iconColor: '#c2410c' },
    'Police': { colors: ['#fce7f3', '#fbcfe8'], iconFamily: 'Ionicons', iconName: 'shield-half-outline', iconColor: '#be185d' },
    'PSCs': { colors: ['#e0f2fe', '#bae6fd'], iconFamily: 'Ionicons', iconName: 'newspaper-outline', iconColor: '#0369a1' },
    'Post-Office': { colors: ['#fff7ed', '#fed7aa'], iconFamily: 'Ionicons', iconName: 'mail-outline', iconColor: '#c2410c' },

    // ── Alternate / alias names that may appear in custom exam stages ──
    'Railways': { colors: ['#dcfce7', '#86efac'], iconFamily: 'Ionicons', iconName: 'train-outline', iconColor: '#166534' },
    'RRB': { colors: ['#dcfce7', '#86efac'], iconFamily: 'Ionicons', iconName: 'train-outline', iconColor: '#166534' },
    'IBPS': { colors: ['#fef08a', '#fde047'], iconFamily: 'Ionicons', iconName: 'wallet-outline', iconColor: '#854d0e' },
    'Banking': { colors: ['#fef08a', '#fde047'], iconFamily: 'MaterialCommunityIcons', iconName: 'bank-outline', iconColor: '#854d0e' },
    'Defense': { colors: ['#d1fae5', '#a7f3d0'], iconFamily: 'MaterialCommunityIcons', iconName: 'shield-star', iconColor: '#065f46' },
    'APPSC': { colors: ['#e0f2fe', '#bae6fd'], iconFamily: 'Ionicons', iconName: 'map-outline', iconColor: '#0369a1' },
    'TSPSC': { colors: ['#e0f2fe', '#bae6fd'], iconFamily: 'Ionicons', iconName: 'compass-outline', iconColor: '#0369a1' },
    'UPPSC': { colors: ['#e0f2fe', '#bae6fd'], iconFamily: 'MaterialCommunityIcons', iconName: 'map-search-outline', iconColor: '#0369a1' },
    'ISRO': { colors: ['#ffedd5', '#fed7aa'], iconFamily: 'Ionicons', iconName: 'rocket-outline', iconColor: '#c2410c' },
    'TET': { colors: ['#fefce8', '#fef08a'], iconFamily: 'Ionicons', iconName: 'school-outline', iconColor: '#a16207' },
    'Teaching': { colors: ['#fefce8', '#fef08a'], iconFamily: 'Ionicons', iconName: 'book-outline', iconColor: '#a16207' },

    // ── Default fallback ──
    'default': { colors: ['#f3f4f6', '#e5e7eb'], iconFamily: 'Ionicons', iconName: 'ribbon-outline', iconColor: '#4b5563' },
};

export const getCategoryAsset = (name: string) => {
    if (!name) return CATEGORY_ASSETS['default'];

    // Exact match (case-insensitive)
    const nameUpper = name.toUpperCase();
    for (const key of Object.keys(CATEGORY_ASSETS)) {
        if (key !== 'default' && key.toUpperCase() === nameUpper) return CATEGORY_ASSETS[key];
    }

    // Substring fallback — name contains key OR key contains name
    // e.g. "RRB NTPC" → matches 'RRB'; "Railway" → matches 'Railways' via key.includes(name)
    for (const key of Object.keys(CATEGORY_ASSETS)) {
        if (key === 'default') continue;
        const keyUpper = key.toUpperCase();
        if (nameUpper.includes(keyUpper) || keyUpper.includes(nameUpper)) {
            return CATEGORY_ASSETS[key];
        }
    }

    return CATEGORY_ASSETS['default'];
};
