export const CATEGORY_ASSETS: Record<string, { colors: readonly [string, string, ...string[]]; iconFamily: 'Ionicons' | 'MaterialCommunityIcons' | 'FontAwesome5'; iconName: string; iconColor: string }> = {
    'UPSC': { colors: ['#e0c3fc', '#8ec5fc'], iconFamily: 'MaterialCommunityIcons', iconName: 'bank', iconColor: '#4c1d95' },
    'SSC': { colors: ['#ffecd2', '#fcb69f'], iconFamily: 'Ionicons', iconName: 'briefcase', iconColor: '#c2410c' },
    'Railways': { colors: ['#dcfce7', '#86efac'], iconFamily: 'Ionicons', iconName: 'train', iconColor: '#166534' },
    'RRB': { colors: ['#dcfce7', '#86efac'], iconFamily: 'Ionicons', iconName: 'train', iconColor: '#166534' },
    'IBPS': { colors: ['#fef08a', '#fde047'], iconFamily: 'Ionicons', iconName: 'wallet', iconColor: '#854d0e' },
    'Banking': { colors: ['#fef08a', '#fde047'], iconFamily: 'MaterialCommunityIcons', iconName: 'bank-outline', iconColor: '#854d0e' },

    // State PSCs
    'APPSC': { colors: ['#e0f2fe', '#bae6fd'], iconFamily: 'Ionicons', iconName: 'map', iconColor: '#0369a1' },
    'TSPSC': { colors: ['#e0f2fe', '#bae6fd'], iconFamily: 'Ionicons', iconName: 'compass', iconColor: '#0369a1' },
    'UPPSC': { colors: ['#e0f2fe', '#bae6fd'], iconFamily: 'MaterialCommunityIcons', iconName: 'map-search-outline', iconColor: '#0369a1' },
    'State Exams': { colors: ['#e0f2fe', '#bae6fd'], iconFamily: 'Ionicons', iconName: 'location', iconColor: '#0369a1' },

    // Core Institutions
    'ISRO': { colors: ['#ffedd5', '#fed7aa'], iconFamily: 'Ionicons', iconName: 'rocket', iconColor: '#c2410c' },
    'Indian Oil': { colors: ['#f3e8ff', '#d8b4fe'], iconFamily: 'MaterialCommunityIcons', iconName: 'gas-station', iconColor: '#6b21a8' },

    // Public Safety / Defense
    'Police': { colors: ['#fce7f3', '#fbcfe8'], iconFamily: 'Ionicons', iconName: 'shield-half', iconColor: '#be185d' },
    'Defense': { colors: ['#d1fae5', '#a7f3d0'], iconFamily: 'MaterialCommunityIcons', iconName: 'shield-star', iconColor: '#065f46' },
    'Army': { colors: ['#d1fae5', '#a7f3d0'], iconFamily: 'MaterialCommunityIcons', iconName: 'tank', iconColor: '#065f46' },
    'Navy': { colors: ['#d1fae5', '#a7f3d0'], iconFamily: 'Ionicons', iconName: 'boat', iconColor: '#065f46' },
    'Air Force': { colors: ['#d1fae5', '#a7f3d0'], iconFamily: 'Ionicons', iconName: 'airplane', iconColor: '#065f46' },

    // Teaching
    'TET': { colors: ['#fefce8', '#fef08a'], iconFamily: 'Ionicons', iconName: 'school', iconColor: '#a16207' },
    'Teaching': { colors: ['#fefce8', '#fef08a'], iconFamily: 'Ionicons', iconName: 'book', iconColor: '#a16207' },

    // Default Fallback
    'default': { colors: ['#f3f4f6', '#e5e7eb'], iconFamily: 'Ionicons', iconName: 'ribbon-outline', iconColor: '#4b5563' }
};

export const getCategoryAsset = (name: string) => {
    // Exact match
    if (CATEGORY_ASSETS[name]) return CATEGORY_ASSETS[name];

    // Sub-string fallback match (e.g. if name is "RRB NTPC", it matches 'RRB')
    for (const key of Object.keys(CATEGORY_ASSETS)) {
        if (name.toUpperCase().includes(key.toUpperCase()) && key !== 'default') {
            return CATEGORY_ASSETS[key];
        }
    }

    return CATEGORY_ASSETS['default'];
};
