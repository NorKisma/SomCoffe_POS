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

function toggleEditStockInput() {
    const isService = document.getElementById('editIsServiceSwitch').checked;
    const stockGroup = document.getElementById('editStockInputGroup');
    if (isService) {
        stockGroup.style.opacity = '0.3';
        stockGroup.style.pointerEvents = 'none';
        stockGroup.querySelector('input').value = '0';
    } else {
        stockGroup.style.opacity = '1';
        stockGroup.style.pointerEvents = 'auto';
    }
}

$(document).ready(function () {
    // Edit Product Logic
    $('.edit-product-btn').on('click', function () {
        const id = $(this).data('id');
        const name = $(this).data('name');
        const price = $(this).data('price');
        const stock = $(this).data('stock');
        const cat = $(this).data('cat');
        const isService = $(this).data('service') == '1';

        // Set Form Action
        $('#editProductForm').attr('action', `/products/edit/${id}`);

        // Set Values
        $('#edit_name').val(name);
        $('#edit_price').val(price);
        $('#edit_stock').val(stock);
        $('#edit_category_id').val(cat);
        $('#editIsServiceSwitch').prop('checked', isService);

        toggleEditStockInput();

        // Show Modal
        $('#editProductModal').modal('show');
    });

    // Initialize DataTable
    const table = $('#inventoryTable').DataTable({
        responsive: true,
        dom: '<"d-flex flex-wrap justify-content-between align-items-center mb-4"fB>rt<"d-flex justify-content-between align-items-center mt-4"ip>',
        buttons: [
            {
                extend: 'print',
                text: '<i class="fas fa-print"></i> Daabac',
                className: 'dt-button'
            },
            {
                extend: 'excel',
                text: '<i class="fas fa-file-excel"></i> Excel',
                className: 'dt-button'
            },
            {
                extend: 'pdf',
                text: '<i class="fas fa-file-pdf"></i> PDF',
                className: 'dt-button'
            }
        ],
        pageLength: 10,
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Raadi halkan...",
            lengthMenu: "_MENU_ alaab",
            info: "Xogta: _START_ - _END_ ka mid ah _TOTAL_",
            paginate: {
                next: '<i class="fas fa-chevron-right"></i>',
                previous: '<i class="fas fa-chevron-left"></i>'
            }
        },
        footerCallback: function (row, data, start, end, display) {
            var api = this.api();
            var intVal = (i) => typeof i === 'string' ? i.replace(/[^\d.-]/g, '') * 1 : typeof i === 'number' ? i : 0;

            // Price Total
            var priceTotal = api.column(3, { page: 'current' }).data().reduce(function (acc, val) {
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = val;
                var amountText = tempDiv.querySelector('.prod-price') ? tempDiv.querySelector('.prod-price').textContent : '';
                var b = amountText || String(val).replace(/[^\d.-]/g, '');
                return acc + intVal(b);
            }, 0);

            // Stock Total
            var stockTotal = api.column(4, { page: 'current' }).data().reduce(function (acc, val) {
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = val;
                var stockText = tempDiv.querySelector('.prod-stock') ? tempDiv.querySelector('.prod-stock').textContent : '';
                var b = stockText || String(val).replace(/[^\d.-]/g, '');
                return acc + intVal(b);
            }, 0);

            $(api.column(3).footer()).html('$ ' + priceTotal.toFixed(2));
            $(api.column(4).footer()).html(stockTotal);
        },
        drawCallback: function () {
            $('.progress-bar').each(function () {
                let width = $(this).data('stock-width');
                $(this).css('width', width + '%');
            });
        }
    });

    // Category filtering via DataTables
    $('.cat-filter-btn').on('click', function () {
        const cat = $(this).data('cat');

        $('.cat-filter-btn').removeClass('active btn-primary').addClass('btn-dark');
        $(this).addClass('active btn-primary').removeClass('btn-dark');

        if (cat === "") {
            table.column(1).search('').draw();
        } else {
            table.column(1).search('^' + cat + '$', true, false).draw();
        }
    });

    // Initial stock animation
    setTimeout(() => {
        $('.progress-bar').each(function () {
            let width = $(this).data('stock-width');
            $(this).css('width', width + '%');
        });
    }, 500);
});