$(document).ready(function() {

    // ══════════════════════════════════════════════
    //  TERMINAL OBJECT — POS Core Logic
    // ══════════════════════════════════════════════
    const Terminal = window.Terminal = {
        cart: [],
        tableId: null,
        _fromPayNow: false,   // set true when table modal opened via PAY NOW

        // ── Step 2: Add product to cart ──
        add: function(id, name, price) {
            id = parseInt(id);
            price = parseFloat(price);
            const existing = this.cart.find(i => i.id === id);
            if (existing) {
                existing.qty += 1;
            } else {
                this.cart.push({ id, name, price, qty: 1 });
            }
            this.render();
            this.flashCartBadge();
        },

        flashCartBadge: function() {
            const $fab = $('.mobile-cart-toggle');
            $fab.css('transform', 'scale(1.3)');
            setTimeout(() => $fab.css('transform', ''), 200);
        },

        changeQty: function(id, delta) {
            id = parseInt(id);
            const item = this.cart.find(i => i.id === id);
            if (!item) return;
            item.qty += delta;
            if (item.qty <= 0) {
                this.cart = this.cart.filter(i => i.id !== id);
            }
            this.render();
        },

        clear: function() {
            if (!this.cart.length) return;
            if (!confirm('Ma hubtaa inaad masaxdo dhamaan cart-ka?')) return;
            this.cart = [];
            this.tableId = null;
            this._fromPayNow = false;
            $('#miiskaLabel').text('Dooro Miiska');
            $('.table-option-card').removeClass('selected');
            this.render();
        },

        // ── Step 4: Table selected ──
        selectTable: function(id, num, el) {
            this.tableId = parseInt(id);
            const label = (this.tableId === 0) ? 'TAKEAWAY' : 'TABLE ' + num;
            $('#miiskaLabel').html('<i class="fas fa-check-circle me-1" style="color:#10b981"></i>' + label);
            $('.table-option-card').removeClass('selected');
            $(el).addClass('selected');
            $('#tableModal').modal('hide');

            // Auto-complete if triggered from PAY NOW button
            if (this._fromPayNow) {
                this._fromPayNow = false;
                setTimeout(() => Terminal._doCheckout(), 350);
            }
        },

        // ── Step 3: Payment method clicked ──
        complete: function(paymentMethod) {
            if (!this.cart.length) {
                return this.showToast('⚠ Dooro alaabta horta!', 'warning');
            }
            if (!paymentMethod) {
                paymentMethod = 'Pending';
            }
            this.currentPaymentMethod = paymentMethod;

            if (this.tableId === null) {
                this._fromPayNow = true;
                $('#tableModal').modal('show');
                return;
            }
            this._doCheckout(this.currentPaymentMethod);
        },

        // ── Internal: Send order to server ──
        _doCheckout: function(paymentMethod) {
            const self = this;
            const $btns = $('.payment-btn, .pay-order-btn');
            $btns.prop('disabled', true);

            const payload = {
                items: self.cart.map(i => ({ id: i.id, qty: i.qty, price: i.price })),
                table_id: self.tableId,
                payment_method: paymentMethod || self.currentPaymentMethod
            };

            fetch('/pos/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(r => r.json())
            .then(d => {
                $btns.prop('disabled', false);
                if (d.success) {
                    self.showToast('✓ Order waa la diray!', 'success');
                    self.cart = [];
                    self.tableId = null;
                    self._fromPayNow = false;
                    self.currentPaymentMethod = null;
                    $('#miiskaLabel').text('Dooro Miiska');
                    $('.table-option-card').removeClass('selected');
                    self.render();
                    // Close mobile cart if open
                    if ($('#invoicePanel').hasClass('show')) toggleCart();
                } else {
                    self.showToast('Cillad: ' + (d.message || 'Unknown error'), 'error');
                }
            })
            .catch(err => {
                $btns.prop('disabled', false);
                console.error('Checkout error:', err);
                self.showToast('Server xiriir la\'aani jirto. Dib u isku day!', 'error');
            });
        },

        showToast: function(msg, type) {
            const bg = { success: '#10b981', warning: '#f59e0b', error: '#ef4444' };
            const $el = $(`<div style="
                position:fixed; bottom:30px; left:50%; transform:translateX(-50%);
                z-index:9999; background:${bg[type]||bg.error}; color:#fff;
                padding:14px 28px; border-radius:16px; font-weight:800;
                font-size:1rem; box-shadow:0 10px 30px rgba(0,0,0,0.3);
                white-space:nowrap; transition:opacity .3s;
            ">${msg}</div>`).appendTo('body');
            setTimeout(() => $el.css('opacity', 0), 2200);
            setTimeout(() => $el.remove(), 2500);
        },

        render: function() {
            const self = this;
            const $body = $('#posInvoiceItems');
            const cur = window.POS_CONFIG.currency;
            let totalQty = 0;

            if (!self.cart.length) {
                $body.html(`
                    <div class="text-center" style="margin-top:60px;opacity:0.35;">
                        <i class="fas fa-shopping-basket fa-4x d-block mb-3"></i>
                        <p class="fw-800 text-uppercase" style="letter-spacing:2px;font-size:.8rem;">Cart waa maran yahay</p>
                    </div>`);
                $('#mobileCartCount').text(0);
                self.updateTotals(0);
                return;
            }

            let html = '';
            let sub = 0;

            self.cart.forEach(function(item) {
                sub += item.price * item.qty;
                totalQty += item.qty;
                html += `
                <div class="invoice-row">
                    <div class="invoice-item-info">
                        <span class="name" style="display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${item.name}</span>
                        <span class="price">${cur}${item.price.toFixed(2)} × ${item.qty}</span>
                    </div>
                    <div class="qty-controls">
                        <div class="qty-btn-circle" onclick="Terminal.changeQty(${item.id}, -1)">−</div>
                        <span style="font-weight:900;color:#e2e8f0;min-width:22px;text-align:center;">${item.qty}</span>
                        <div class="qty-btn-circle" onclick="Terminal.changeQty(${item.id}, 1)">+</div>
                        <span style="font-weight:900;color:#a5f3fc;min-width:62px;text-align:right;">${cur}${(item.price*item.qty).toFixed(2)}</span>
                    </div>
                </div>`;
            });

            $body.html(html);
            $('#mobileCartCount').text(totalQty);
            self.updateTotals(sub);
        },

        updateTotals: function(sub) {
            const vatRate = parseFloat(window.POS_CONFIG.vatRate) / 100;
            const tax = sub * vatRate;
            const total = sub + tax;
            const cur = window.POS_CONFIG.currency;
            $('#vSubtotal').text(cur + sub.toFixed(2));
            $('#vTax').text(cur + tax.toFixed(2));
            $('#vTotal').text(cur + total.toFixed(2));
        }
    };

    // ══════════════════════════════════════════════
    //  GLOBAL HELPERS
    // ══════════════════════════════════════════════
    window.toggleCart = function() {
        $('#invoicePanel').toggleClass('show');
    };

    // ── Step 1: Category filter ──
    $(document).on('click', '#posCatNav .nav-cat-item', function() {
        $('#posCatNav .nav-cat-item').removeClass('active');
        $(this).addClass('active');
        applyFilters();
    });

    // ── Step 4: Table card click ──
    $(document).on('click', '.table-option-card', function() {
        const id  = parseInt($(this).data('id'));
        const num = String($(this).data('num'));
        Terminal.selectTable(id, num, this);
    });

    // ── Search filter (works with active category) ──
    function applyFilters() {
        const query = $('#megaSearch').val().toLowerCase().trim();
        const activeCat = $('#posCatNav .nav-cat-item.active').data('cat');
        $('.product-item-wrapper').each(function() {
            const itemCat  = $(this).attr('data-cat');
            const itemName = $(this).find('.product-title').text().toLowerCase();
            const catOk    = (activeCat === '__all__' || itemCat === activeCat);
            const nameOk   = (query === '' || itemName.includes(query));
            $(this).toggle(catOk && nameOk);
        });
    }

    $('#megaSearch').on('input', applyFilters);

    // ── Step 2: Product click ──
    $(document).on('click', '.product-item-btn', function() {
        const $el  = $(this);
        const id   = $el.data('id');
        const name = $el.data('name');
        const price = $el.data('price');
        Terminal.add(id, name, price);

        // Visual ripple on card
        $el.addClass('active-press');
        setTimeout(() => $el.removeClass('active-press'), 180);
    });

    // Initial render
    Terminal.render();
});