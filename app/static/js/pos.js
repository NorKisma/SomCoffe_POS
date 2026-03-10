$(document).ready(function () {

    // ══════════════════════════════════════════════
    //  TERMINAL OBJECT — POS Core Logic
    // ══════════════════════════════════════════════
    const Terminal = window.Terminal = {
        cart: [],
        tableId: null,
        customerId: null,
        _fromPayNow: false,   // set true when table modal opened via PAY NOW
        appendingOrderId: null,
        pinBuffer: "",
        lockTimer: null,
        isLocked: false,

        // ── Step 2: Add product to cart ──
        add: function (id, name, price) {
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

        flashCartBadge: function () {
            const $fab = $('.mobile-cart-toggle');
            $fab.css('transform', 'scale(1.3)');
            setTimeout(() => $fab.css('transform', ''), 200);
        },

        changeQty: function (id, delta) {
            id = parseInt(id);
            const item = this.cart.find(i => i.id === id);
            if (!item) return;
            item.qty += delta;
            if (item.qty <= 0) {
                this.cart = this.cart.filter(i => i.id !== id);
            }
            this.render();
        },

        clear: function () {
            if (!this.cart.length) return;
            if (!confirm('Ma hubtaa inaad masaxdo dhamaan cart-ka?')) return;
            this.cart = [];
            this.tableId = null;
            this.customerId = null;
            this.appendingOrderId = null;
            this._fromPayNow = false;
            $('#miiskaLabel').text('Dooro Miiska');
            $('#customerLabel').text('Macmiil');
            $('.table-option-card').removeClass('selected');
            this.render();
        },

        selectCustomer: function (id, name) {
            this.customerId = parseInt(id);
            const label = (this.customerId === 0) ? 'Macmiil' : name;
            $('#customerLabel').html(label);
            $('#customerModal').modal('hide');
        },

        quickAddCustomer: function () {
            const name = $('#q_name').val().trim();
            const phone = $('#q_phone').val().trim();
            const self = this;

            if (!name) return self.showToast('⚠ Fadlan geli magaca!', 'warning');

            fetch('/pos/add_customer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
                },
                body: JSON.stringify({ name, phone })
            })
                .then(r => r.json())
                .then(d => {
                    if (d.success) {
                        self.showToast('✓ Macmiilka waa la keydiyay!', 'success');
                        // Add to list UI
                        const newHtml = `
                    <div class="customer-option-item" data-id="${d.customer.id}" data-name="${d.customer.name}" style="padding: 12px; border-radius: 12px; cursor: pointer; margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.05);">
                        <div class="fw-bold">${d.customer.name} ${d.customer.phone ? '(' + d.customer.phone + ')' : ''}</div>
                    </div>`;
                        $('.customer-list').prepend(newHtml);

                        // Select him
                        self.selectCustomer(d.customer.id, d.customer.name);

                        // Reset form
                        $('#q_name').val('');
                        $('#q_phone').val('');
                        $('#quickAddForm').hide();
                    } else {
                        self.showToast('Cillad: ' + d.message, 'error');
                    }
                })
                .catch(err => {
                    console.error(err);
                    self.showToast('Server error during quick add.', 'error');
                });
        },

        // ── Step 4: Table selected ──
        selectTable: function (id, num, el) {
            const self = this;
            this.tableId = parseInt(id);
            const label = (this.tableId === 0) ? 'TAKEAWAY' : 'TABLE ' + num;
            $('#miiskaLabel').html('<i class="fas fa-check-circle me-1" style="color:#10b981"></i>' + label);
            $('.table-option-card').removeClass('selected');
            $(el).addClass('selected');

            // Check if table has an active pending order
            if (this.tableId !== 0) {
                fetch(`/pos/check_table/${this.tableId}`)
                    .then(r => r.json())
                    .then(d => {
                        if (d.exists) {
                            $(el).addClass('occupied');
                            Swal.fire({
                                title: 'Dalab Hore!',
                                html: `Miiskan (Table ${num}) dalab ayaa horey u saaraa (#${String(d.order_id).padStart(6, '0')}).<br>Ma rabtaa inaad <b>ku darto</b> dalabkan?`,
                                icon: 'info',
                                showCancelButton: true,
                                confirmButtonColor: '#10b981',
                                cancelButtonColor: '#64748b',
                                confirmButtonText: 'Haa, Ku dar',
                                cancelButtonText: 'Maya, Hubi'
                            }).then((result) => {
                                if (result.isConfirmed) {
                                    self.appendingOrderId = d.order_id;
                                    self.showToast(`Waxa lagu darayaa dalabka #${String(d.order_id).padStart(6, '0')}`, 'success');
                                    $('#miiskaLabel').append(` <span class="badge bg-success" style="font-size:0.6rem;">APPENDING #${d.order_id}</span>`);
                                } else {
                                    self.appendingOrderId = null;
                                    self.tableId = null;
                                    $('#miiskaLabel').text('Dooro Miiska');
                                    $('.table-option-card').removeClass('selected');
                                }
                            });
                        } else {
                            self.appendingOrderId = null;
                        }
                    });
            } else {
                this.appendingOrderId = null;
            }

            $('#tableModal').modal('hide');

            // Auto-complete if triggered from PAY NOW button
            if (this._fromPayNow) {
                this._fromPayNow = false;
                if (this._splitData) {
                    const { paid, credit, method } = this._splitData;
                    this._splitData = null;
                    setTimeout(() => Terminal._doSplitCheckout(paid, credit, method), 350);
                } else {
                    setTimeout(() => Terminal._doCheckout(), 350);
                }
            }
        },

        // ── Step 3: Payment method clicked ──
        complete: function (paymentMethod) {
            if (!this.cart.length) {
                return this.showToast('⚠ Dooro alaabta horta!', 'warning');
            }
            if (!paymentMethod) {
                paymentMethod = 'Pending';
            }
            this.currentPaymentMethod = paymentMethod;

            if (paymentMethod === 'Credit' && (this.customerId === null || this.customerId === 0)) {
                this.showToast('⚠ Fadlan dooro macmiilka deynta loo qorayo!', 'warning');
                $('#customerModal').modal('show');
                return;
            }

            if (this.tableId === null) {
                this._fromPayNow = true;
                $('#tableModal').modal('show');
                return;
            }
            this._doCheckout(this.currentPaymentMethod);
        },

        // ── Internal: Send order to server ──
        _doCheckout: function (paymentMethod) {
            const self = this;
            const $btns = $('.payment-btn, .pay-order-btn');
            $btns.prop('disabled', true);

            const payload = {
                items: self.cart.map(i => ({ id: i.id, qty: i.qty, price: i.price })),
                table_id: self.tableId,
                customer_id: self.customerId,
                payment_method: paymentMethod || self.currentPaymentMethod,
                order_id: self.appendingOrderId
            };

            fetch('/pos/checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
                },
                body: JSON.stringify(payload)
            })
                .then(r => r.json())
                .then(d => {
                    $btns.prop('disabled', false);
                    if (d.success) {
                        self.showToast('✓ Order waa la diray!', 'success');
                        self.cart = [];
                        self.tableId = null;
                        self.customerId = null;
                        self._fromPayNow = false;
                        self.currentPaymentMethod = null;
                        $('#miiskaLabel').text('Dooro Miiska');
                        $('#customerLabel').text('Macmiil');
                        $('.table-option-card').removeClass('selected');
                        self.render();
                        if ($('#invoicePanel').hasClass('show')) toggleCart();

                        if (d.order_id) {
                            const printUrl = window.location.origin + '/orders/print/' + d.order_id;
                            window.location.href = printUrl;
                        }
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

        showToast: function (msg, type) {
            const bg = { success: '#10b981', warning: '#f59e0b', error: '#ef4444' };
            const $el = $(`<div style="
                position:fixed; bottom:30px; left:50%; transform:translateX(-50%);
                z-index:9999; background:${bg[type] || bg.error}; color:#fff;
                padding:14px 28px; border-radius:16px; font-weight:800;
                font-size:1rem; box-shadow:0 10px 30px rgba(0,0,0,0.3);
                white-space:nowrap; transition:opacity .3s;
            ">${msg}</div>`).appendTo('body');
            setTimeout(() => $el.css('opacity', 0), 2200);
            setTimeout(() => $el.remove(), 2500);
        },

        openSplitModal: function () {
            if (!this.cart.length) return this.showToast('⚠ Dooro alaabta horta!', 'warning');

            const total = this.calculateTotal();
            $('#splitTotalLabel').text(window.POS_CONFIG.currency + total.toFixed(2));
            $('#split_paid').val(total.toFixed(2));
            $('#split_credit').val('0.00');

            // Check if customer set for credit
            if (this.customerId === null || this.customerId === 0) {
                $('#splitWarning').show();
            } else {
                $('#splitWarning').hide();
            }

            $('#splitModal').modal('show');
        },

        calculateTotal: function () {
            let sub = this.cart.reduce((s, i) => s + (i.price * i.qty), 0);
            const vatRate = parseFloat(window.POS_CONFIG.vatRate) / 100;
            return sub * (1 + vatRate);
        },

        submitSplit: function () {
            const paid = parseFloat($('#split_paid').val()) || 0;
            const credit = parseFloat($('#split_credit').val()) || 0;
            const method = $('#split_method').val();
            const total = this.calculateTotal();

            if (credit > 0 && (this.customerId === null || this.customerId === 0)) {
                this.showToast('⚠ Macmiil dooro hadaad deyn qorayso!', 'warning');
                $('#splitModal').modal('hide');
                $('#customerModal').modal('show');
                return;
            }

            if (this.tableId === null) {
                this._fromPayNow = true;
                this._splitData = { paid, credit, method }; // Save for later
                $('#splitModal').modal('hide');
                $('#tableModal').modal('show');
                return;
            }

            this._doSplitCheckout(paid, credit, method);
        },

        _doSplitCheckout: function (paid, credit, method) {
            const self = this;
            const payload = {
                items: self.cart.map(i => ({ id: i.id, qty: i.qty, price: i.price })),
                table_id: self.tableId,
                customer_id: self.customerId,
                split_payment: {
                    paid_amount: paid,
                    credit_amount: credit,
                    paid_method: method
                },
                order_id: self.appendingOrderId
            };

            fetch('/pos/checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
                },
                body: JSON.stringify(payload)
            })
                .then(r => r.json())
                .then(d => {
                    if (d.success) {
                        $('#splitModal').modal('hide');
                        self.showToast('✓ Split order waa la diray!', 'success');
                        self.cart = [];
                        self.tableId = null;
                        self.customerId = null;
                        self._fromPayNow = false;
                        $('#miiskaLabel').text('Dooro Miiska');
                        $('#customerLabel').text('Macmiil');
                        $('.table-option-card').removeClass('selected');
                        self.render();
                        if ($('#invoicePanel').hasClass('show')) toggleCart();

                        // Auto-open print page
                        if (d.order_id) {
                            const printUrl = window.location.origin + '/orders/print/' + d.order_id;
                            window.location.href = printUrl;
                        }
                    } else {
                        self.showToast('Cillad: ' + d.message, 'error');
                    }
                });
        },

        render: function () {
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

            self.cart.forEach(function (item) {
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
                        <span style="font-weight:900;color:#a5f3fc;min-width:62px;text-align:right;">${cur}${(item.price * item.qty).toFixed(2)}</span>
                    </div>
                </div>`;
            });

            $body.html(html);
            $('#mobileCartCount').text(totalQty);
            self.updateTotals(sub);
        },

        updateTotals: function (sub) {
            const vatRate = parseFloat(window.POS_CONFIG.vatRate) / 100;
            const tax = sub * vatRate;
            const total = sub + tax;
            const cur = window.POS_CONFIG.currency;

            $('#vSubtotal').text(cur + sub.toFixed(2));
            $('#vTax').text(cur + tax.toFixed(2));

            const $total = $('#vTotal');
            $total.text(cur + total.toFixed(2));

            // Add pulse effect
            $total.addClass('amount-pulse');
            setTimeout(() => $total.removeClass('amount-pulse'), 500);
        },

        // ── Lock Screen Logic ──
        pinPress: function (num) {
            if (this.pinBuffer.length < 6) {
                this.pinBuffer += num;
                this.updatePinDisplay();
            }
        },
        pinClear: function () {
            this.pinBuffer = "";
            this.updatePinDisplay();
        },
        updatePinDisplay: function () {
            const dots = "•".repeat(this.pinBuffer.length) || "••••";
            $('#pinDisplay').text(dots);
        },
        pinSubmit: function () {
            const self = this;
            if (!self.pinBuffer) return;

            const formData = new FormData();
            formData.append('pin', self.pinBuffer);
            formData.append('csrf_token', $('meta[name="csrf-token"]').attr('content'));

            fetch('/auth/verify-pin', {
                method: 'POST',
                body: formData
            })
                .then(r => r.json())
                .then(d => {
                    if (d.success) {
                        self.unlock();
                    } else {
                        self.showToast('⚠ PIN-ka waa khalad!', 'error');
                        self.pinClear();
                    }
                })
                .catch(err => {
                    console.error(err);
                    self.showToast('PIN verification error.', 'error');
                });
        },
        lock: function () {
            this.isLocked = true;
            this.pinClear();
            $('#lockScreen').fadeIn();
        },
        unlock: function () {
            this.isLocked = false;
            $('#lockScreen').fadeOut();
            this.resetLockTimer();
        },
        resetLockTimer: function () {
            const self = this;
            if (this.lockTimer) clearTimeout(this.lockTimer);

            const timeoutMs = (window.POS_CONFIG.sessionTimeout || 5) * 60 * 1000;

            this.lockTimer = setTimeout(() => {
                if (!self.isLocked) self.lock();
            }, timeoutMs);
        }
    };

    // ══════════════════════════════════════════════
    //  GLOBAL HELPERS
    // ══════════════════════════════════════════════
    window.toggleCart = function () {
        $('#invoicePanel').toggleClass('show');
    };

    // ── Step 1: Category filter ──
    $(document).on('click', '#posCatNav .nav-cat-item', function () {
        $('#posCatNav .nav-cat-item').removeClass('active');
        $(this).addClass('active');
        applyFilters();
    });

    // ── Step 4: Table card click ──
    $(document).on('click', '.table-option-card', function () {
        const id = parseInt($(this).data('id'));
        const num = String($(this).data('num'));
        Terminal.selectTable(id, num, this);
    });

    // ── Search filter (works with active category) ──
    function applyFilters() {
        const query = $('#megaSearch').val().toLowerCase().trim();
        const activeCat = $('#posCatNav .nav-cat-item.active').data('cat');
        $('.product-item-wrapper').each(function () {
            const itemCat = $(this).attr('data-cat');
            const itemName = $(this).find('.product-title').text().toLowerCase();
            const catOk = (activeCat === '__all__' || itemCat === activeCat);
            const nameOk = (query === '' || itemName.includes(query));
            $(this).toggle(catOk && nameOk);
        });
    }

    $('#megaSearch').on('input', applyFilters);

    // ── Step 2: Product click ──
    $(document).on('click', '.product-item-btn', function () {
        const $el = $(this);
        const id = $el.data('id');
        const name = $el.data('name');
        const price = $el.data('price');
        Terminal.add(id, name, price);

        // Visual ripple on card
        $el.addClass('active-press');
        setTimeout(() => $el.removeClass('active-press'), 180);
    });

    // ── Customer option click ──
    $(document).on('click', '.customer-option-item', function () {
        const id = $(this).data('id');
        const name = $(this).data('name');
        Terminal.selectCustomer(id, name);
    });

    // ── Customer search ──
    $('#customerSearch').on('input', function () {
        const query = $(this).val().toLowerCase().trim();
        $('.customer-option-item').each(function () {
            const name = $(this).data('name').toLowerCase();
            $(this).toggle(name.includes(query));
        });
    });

    // ── Split Modal Calculation ──
    $('#split_paid').on('input', function () {
        const total = Terminal.calculateTotal();
        const paid = parseFloat($(this).val()) || 0;
        const credit = Math.max(0, total - paid);
        $('#split_credit').val(credit.toFixed(2));
    });

    // ── On Load: Check for append_order_id in URL ──
    const urlParams = new URLSearchParams(window.location.search);
    const appendId = urlParams.get('append_order_id');
    const tableId = urlParams.get('table_id');
    const tableNum = urlParams.get('table_num');
    if (appendId) {
        Terminal.appendingOrderId = parseInt(appendId);
        Terminal.tableId = parseInt(tableId);
        const tableName = (Terminal.tableId === 0) ? 'TAKEAWAY' : 'TABLE ' + tableNum;
        $('#miiskaLabel').html(`<i class="fas fa-check-circle me-1" style="color:#10b981"></i>${tableName} <span class="badge bg-success" style="font-size:0.6rem;">APPENDING #${String(appendId).padStart(6, '0')}</span>`);
        $(`.table-option-card[data-id="${tableId}"]`).addClass('selected');
        Terminal.showToast(`Appending to Order #${appendId}`, 'success');
    }

    // ── Initial render and Lock Timer ──
    Terminal.render();
    Terminal.resetLockTimer();

    // ── Activity Listeners for Lock Timer ──
    $(document).on('mousedown mousemove keydown scroll touchstart', function () {
        if (!Terminal.isLocked) Terminal.resetLockTimer();
    });
});