function toggleStockInput() {
    const isService = document.getElementById('isServiceSwitch').checked;
    const stockGroup = document.getElementById('stockInputGroup');
    if (isService) {
        stockGroup.style.opacity = '0.3';
        stockGroup.style.pointerEvents = 'none';
        stockGroup.querySelector('input').value = '0';
    } else {
        stockGroup.style.opacity = '1';
        stockGroup.style.pointerEvents = 'auto';
    }
}

$(document).ready(function() {
    // Inventory Progress Bars
    $('.progress-bar').each(function() {
        let width = $(this).data('stock-width');
        $(this).animate({ width: width + '%' }, 1000);
    });

    // Filtering Logic
    function filterInventory() {
        const searchText = $('#inventorySearch').val().toLowerCase();
        const activeCat = $('.cat-filter-btn.active').data('cat');

        $('.inventory-row').each(function() {
            const rowCat = $(this).data('cat');
            const rowName = $(this).find('.product-name-heading').text().toLowerCase();
            
            const matchesCat = (activeCat === 'all' || rowCat === activeCat);
            const matchesSearch = rowName.includes(searchText);

            if (matchesCat && matchesSearch) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    }

    // Category button click
    $('.cat-filter-btn').on('click', function() {
        $('.cat-filter-btn').removeClass('active btn-primary').addClass('btn-dark');
        $(this).addClass('active btn-primary').removeClass('btn-dark');
        filterInventory();
    });

    // Search input
    $('#inventorySearch').on('input', function() {
        filterInventory();
    });
});