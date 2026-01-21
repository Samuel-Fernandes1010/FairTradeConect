$(function() {
	const form = $("form[action*='adicionar_carrinho']");
	if (form.length) {
		form.on('submit', function(e) {
			e.preventDefault();
			const data = form.serialize();
			$.post(form.attr('action'), data, function(resp) {
				if (resp.success) {
					$("#modal-carrinho").fadeIn();
				} else {
					alert(resp.message || 'Erro ao adicionar ao carrinho.');
				}
			});
		});
		$("#continuar-comprando").on('click', function() {
			$("#modal-carrinho").fadeOut();
		});
	}
});
