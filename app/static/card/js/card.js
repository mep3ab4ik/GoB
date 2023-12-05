(function ($) {
    $(document).ready(() => {
        let objectTools = $('.grp-object-tools');
        let cardId = objectTools.find("a[href*='history']").attr('href').split('/').at(-3);
        let editions = ['regular', 'shiny'];
        editions.forEach(edition =>
            objectTools.append(`<li><a href="/api/v1/card/bake/${cardId}/${edition}/" target="_blank">Bake ${edition}</a></li>`)
        );
    })
})(django.jQuery);