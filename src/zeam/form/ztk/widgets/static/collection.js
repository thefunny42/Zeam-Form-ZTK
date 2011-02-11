
// Requires: json-template.js

(function ($){

    var field_name_regexp = /(.*)\.field\.(\d+)$/;

    var increment = function(value) {
        return (parseInt(value) + 1).toString();
    };

    var create_template = function(node) {
        var identifier = node.attr('rel');
        var template = new jsontemplate.Template(
            node.get(0).innerHTML, {
                // For the moment this use an hijack version of
                // json-template.
                'undefined-str': function(name){
                    return '{' + name + '}';
                }
            });

        // Remove the template from the DOM.
        node.html('');
        // Return an object that let you render the template
        return {
            identifier:identifier,
            template:template,
            render: function(identifier) {
                var parameters = {};
                parameters[this.identifier] = identifier;

                var data = $(this.template.expand(parameters));
                if (!data.is('.field-collection-line')) {
                    return data.find('.field-collection-line:first');
                };
                return data;
            }
        };
    };

    var starts_with = function(string) {
        var starter = '^';

        for (var i= 1; i < arguments.length; i++) {
            starter += arguments[i];
        };
        return string.match(starter);
    };

    var update_line_names = function(line, base_name, count) {
        var selector_name = base_name + '.checked.';
        var present_name = base_name + '.present.';
        var field_name = base_name + '.field.';

        var rewriter = function () {
            var input = $(this);
            var old_name = input.attr('name');

            if (starts_with(old_name, selector_name)) {
                input.attr('name', selector_name + count);
            } else if (starts_with(old_name, present_name)) {
                input.attr('name', present_name + count);
            } else if (starts_with(old_name, field_name)) {
                var new_name = field_name + count;
                var i = field_name.length;

                // Consume the old count
                for (; i < old_name.length && old_name[i] != '.'; i++);
                // Copy the end of the old name to the new one
                for (; i < old_name.length; i++) {
                    new_name += old_name[i];
                };
                input.attr('name', new_name);
            };
        };
        // Rewrite name for input, textarea and select tags.
        line.find('input').each(rewriter);
        line.find('textarea').each(rewriter);
        line.find('select').each(rewriter);

        // Update the rel attribute on the file.
        line.attr('rel', field_name + count);
    };

    var update_move_buttons = function(line_top, line_bottom) {
        // Show or hide move up/down button depending if it is the
        // first line or last line or not. This code exist because IE
        // 7 doesn't support last-child in CSS.
        if (line_top.is(':first-child')) {
            line_top.find('.field-collection-move-up').hide();
            line_bottom.find('.field-collection-move-up').show();
        };
        if (line_bottom.is(':last-child')) {
            line_top.find('.field-collection-move-down').show();
            line_bottom.find('.field-collection-move-down').hide();
        };
    };

    $(document).ready(function (){
        $('form.zeam-form div.field-collection').each(function (){
            var field = $(this);
            var counter = field.find('input.field-collection-counter');
            var container = field.find('.field-collection-lines:first');
            var template = create_template(field.find('.field-collection-template:first'));

            // Clear style on any existing buttons.
            update_move_buttons(
                container.find('.field-collection-line:first'),
                container.find('.field-collection-line:last'));

            // Bind the add button
            field.find('.field-collection-add-line').live('click', function() {
                var identifier = counter.val();
                var new_line = template.render(identifier);
                var empty_message = field.find('.field-collection-empty');
                var remove_button = field.find('.field-collection-remove-line');
                var previous_line = container.children('.field-collection-line:last');

                if (empty_message.is(':visible')) {
                    empty_message.slideUp();
                };
                if (!remove_button.is(':visible')) {
                    remove_button.fadeIn();
                };
                if (!previous_line.length) {
                    previous_line = new_line;
                };
                update_move_buttons(previous_line, new_line);
                new_line.appendTo(container);
                counter.val(increment(identifier));
                return false;
            });

            // Bind the remove button
            field.find('.field-collection-remove-line').live('click', function() {
                field.find('input.field-collection-line-selector:checked').each(function (){
                    var line = $(this).parents('.field-collection-line');
                    var previous_line = line.prev('.field-collection-line');
                    var next_line = line.next('.field-collection-line');

                    line.remove();

                    update_move_buttons(next_line, previous_line);

                    var lines = container.find('.field-collection-line');

                    if (!lines.length) {
                        var empty_message = field.find('.field-collection-empty');
                        var remove_button = field.find('.field-collection-remove-line');

                        empty_message.slideDown();
                        remove_button.fadeOut();
                    };
                });
                return false;
            });

            // Bind the up button
            field.find('.field-collection-move-up').live('click', function () {
                var button = $(this);
                var line = button.parents('.field-collection-line');
                var previous_line = line.prev();

                if (previous_line.hasClass('field-collection-line')) {
                    var name_info = field_name_regexp.exec(line.attr('rel'));
                    var base_name = name_info[1];
                    var count = name_info[2];

                    var previous_name_info = field_name_regexp.exec(
                        previous_line.attr('rel'));
                    var previous_count = previous_name_info[2];

                    line.remove();
                    line.insertBefore(previous_line);
                    update_line_names(line, base_name, previous_count);
                    update_line_names(previous_line, base_name, count);
                    update_move_buttons(line, previous_line);
                };
                return false;
            });

            // Bind the down button
            field.find('.field-collection-move-down').live('click', function () {
                var button = $(this);
                var line = button.parents('.field-collection-line');
                var next_line = line.next();

                if (next_line.hasClass('field-collection-line')) {
                    var name_info = field_name_regexp.exec(line.attr('rel'));
                    var base_name = name_info[1];
                    var count = name_info[2];

                    var next_name_info = field_name_regexp.exec(next_line.attr('rel'));
                    var next_count = next_name_info[2];

                    line.remove();
                    line.insertAfter(next_line);
                    update_line_names(line, base_name, next_count);
                    update_line_names(next_line, base_name, count);
                    update_move_buttons(next_line, line);
                };
                return false;
            });
        });
    });
})(jQuery);
