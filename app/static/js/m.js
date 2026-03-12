$(document).on('click', '.plus-cart', function () {
    var id = $(this).attr("pid").toString();
    var size = $(this).attr("psize").toString();
    var eml = $(`.quantity-value[data-product="${id}"][data-size="${size}"]`);
    $.ajax({
        type: "GET",
        url: "/pluscart",
        data: {
            prod_id: id,
            size: size
        },
        success: function (data) {
            if (data.error) {
                alert(data.error);
            }
            eml.text(data.quantity);
            $("#amount").text("₹" + data.amount);
            if (data.shipping_fee === 0) {
                $("#logistics_fee").text("Free Delivery");
            } else {
                $("#logistics_fee").text("₹" + data.shipping_fee + ".00");
            }
            $("#totalamount").text("₹" + data.totalamount);
        }
    })
});

$(document).on('click', '.minus-cart', function () {
    var id = $(this).attr("pid").toString();
    var size = $(this).attr("psize").toString();
    var eml = $(`.quantity-value[data-product="${id}"][data-size="${size}"]`);
    $.ajax({
        type: "GET",
        url: "/minuscart",
        data: {
            prod_id: id,
            size: size
        },
        success: function (data) {
            eml.text(data.quantity);
            $("#amount").text("₹" + data.amount);
            if (data.shipping_fee === 0) {
                $("#logistics_fee").text("Free Delivery");
            } else {
                $("#logistics_fee").text("₹" + data.shipping_fee + ".00");
            }
            $("#totalamount").text("₹" + data.totalamount);
        }
    })
});

$(document).on('click', '.remove-cart', function () {
    var id = $(this).attr("pid").toString();
    var size = $(this).attr("psize").toString();
    var itemRow = $(`.cart-item-row[data-item-id="${id}"][psize="${size}"]`);
    if (itemRow.length === 0) {
        // Fallback for session items if needed or just use id/size properly
        itemRow = $(this).closest('.cart-item-row');
    }
    $.ajax({
        type: "GET",
        url: "/removecart",
        data: {
            prod_id: id,
            size: size
        },
        success: function (data) {
            $("#amount").text("₹" + data.amount);
            if (data.shipping_fee === 0) {
                $("#logistics_fee").text("Free Delivery");
            } else {
                $("#logistics_fee").text("₹" + data.shipping_fee + ".00");
            }
            $("#totalamount").text("₹" + data.totalamount);
            itemRow.fadeOut(300, function () {
                $(this).remove();
                if ($('.cart-item-row').length == 0) {
                    window.location.reload();
                }
            });
        }
    })
});

// $('.plus-wishlist').click(function(){
//     var id=$(this).attr("pid").toString();
//     $.ajax({
//         type:"GET",
//         url:"/pluswishlist",
//         data:{
//             prod_id:id
//         },
//         success:function(data){
//             //alert(data.message)
//             window.location.href = `http://127.0.0.1:8000/product-detail/${id}`
//         }
//     })
// })


// $('.minus-wishlist').click(function(){
//     var id=$(this).attr("pid").toString();
//     $.ajax({
//         type:"GET",
//         url:"/minuswishlist",
//         data:{
//             prod_id:id
//         },
//         success:function(data){
//             window.location.href = `http://127.0.0.1:8000/product-detail/${id}`
//         }
//     })
// })
