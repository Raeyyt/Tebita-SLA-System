const ensureUTC = (dateString: string): Date => {
    // If string doesn't end with Z and doesn't have offset, assume UTC and append Z
    if (dateString && !dateString.endsWith('Z') && !/[+-]\d{2}:\d{2}$/.test(dateString)) {
        return new Date(dateString + 'Z');
    }
    return new Date(dateString);
};

export const formatDate = (dateString: string | null | undefined): string => {
    if (!dateString) return 'N/A';
    try {
        const date = ensureUTC(dateString);
        // Check if date is valid
        if (isNaN(date.getTime())) return 'Invalid Date';

        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    } catch (error) {
        console.error('Error formatting date:', error);
        return 'Error';
    }
};

export const formatTime = (dateString: string | null | undefined): string => {
    if (!dateString) return 'N/A';
    try {
        const date = ensureUTC(dateString);
        if (isNaN(date.getTime())) return 'Invalid Time';

        return date.toLocaleString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    } catch (error) {
        return 'Error';
    }
};

export const formatDateOnly = (dateString: string | null | undefined): string => {
    if (!dateString) return 'N/A';
    try {
        const date = ensureUTC(dateString);
        if (isNaN(date.getTime())) return 'Invalid Date';

        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        return 'Error';
    }
};
