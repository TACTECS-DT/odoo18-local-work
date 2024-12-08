(function ($) {
    $.widget("ui.combobox", {
        _create: function() {
            var wrapper = this.wrapper = $("<span />").addClass("ui-combobox")
                , self = this;

            this.element.wrap(wrapper);

            this.element
                .addClass("ui-state-default ui-combobox-input ui-widget ui-widget-content ui-corner-left")
                .autocomplete($.extend({
                    minLength: 0
                }, this.options));

            $("<a />")
                .insertAfter(this.element)
                .button({
                    icons: {
                        primary: "ui-icon-triangle-1-s"
                    },
                    text: false
                })
                .removeClass("ui-corner-all")
                .addClass("ui-corner-right ui-combobox-toggle")
                .click(function () {
                    if (self.element.autocomplete("widget" ).is(":visible")) {
                        self.element.autocomplete("close");
                        return;
                    }

                    $(this).blur();

                    self.element.autocomplete("search", "");
                    self.element.focus();
                });
        },

        destroy: function() {
            this.wrapper.remove();
            $.Widget.prototype.destroy.call(this);
        }
    });
})(jQuery);