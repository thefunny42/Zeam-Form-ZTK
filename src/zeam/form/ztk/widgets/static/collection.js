
// Requires: json-template.js

(function ($){

    var field_name_regexp = /(.*)\.field\.(\d+)$/;

    var increment = function(value) {
        return (parseInt(value) + 1).toString();
    };

    var starts_with = function(string) {
        var starter = '^';

        for (var i= 1; i < arguments.length; i++) {
            starter += arguments[i];
        };
        return string.match(starter);
    };

    var prepare_field = function(field) {
        var container = field.find('.field-collection-lines:first');
        field.data(
            'template',
            create_template(field.children('.field-collection-template')));

        // Clear style on any existing buttons.
        update_move_buttons(
            container.children('.field-collection-line:first'),
            container.children('.field-collection-line:last'));
    };

    var create_template = function(node) {
        if (!node.length) {
            // allowAdding is false;
            return undefined;
        };

        var identifier = node.attr('rel');
        var template = new jsontemplate.Template(
            node.get(0).innerHTML, {
                // For the moment this use an hijack version of
                // json-template.
                undefined_str: function(name){
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
                    data = data.find('.field-collection-line:first');
                };

                // The line might contains other field-collection
                data.find('div.field-collection').each(function (){
                    prepare_field($(this));
                });

                return data;
            }
        };
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
            line_bottom.children('.ordering-actions').children(
                '.field-collection-move-up').show();
            line_top.children('.ordering-actions').children(
                '.field-collection-move-up').hide();
        };
        if (line_bottom.is(':last-child')) {
            line_top.children('.ordering-actions').children(
                '.field-collection-move-down').show();
            line_bottom.children('.ordering-actions').children(
                '.field-collection-move-down').hide();
        };
    };

    $(document).ready(function (){
        $('form.zeam-form div.field-collection').each(function (){
            prepare_field($(this));
        });

        // Bind add buttons
        $('form.zeam-form input.field-collection-add-line').live('click', function() {
            var field = $(this).closest('div.field-collection');
            var counter = field.children('input.field-collection-counter');
            var identifier = counter.val();
            var container = field.find('.field-collection-lines:first');

            var new_line = field.data('template').render(identifier);
            var header_message = field.children('.field-collection-header');
            var empty_message = field.children('.field-collection-empty');
            var actions = field.children('.multi-actions');
            var remove_button = actions.children('.field-collection-remove-line');
            var previous_line = container.children('.field-collection-line:last');

            if (empty_message.is(':visible')) {
                header_message.slideDown();
                empty_message.slideUp();
            };
            if (!remove_button.is(':visible')) {
                remove_button.fadeIn();
            };
            if (!previous_line.length) {
                previous_line = new_line;
            };
            new_line.appendTo(container);
            update_move_buttons(previous_line, new_line);
            counter.val(increment(identifier));
            return false;
        });

        // Bind the remove button
        $('form.zeam-form input.field-collection-remove-line').live('click', function() {
            var field = $(this).closest('div.field-collection');
            var container = field.find('.field-collection-lines:first');
            var selected = container.children(
                '.field-collection-line').children(
                    '.line-actions').children(
                        'input.field-collection-line-selector:checked');

            selected.each(function (){
                var line = $(this).closest('.field-collection-line');
                var previous_line = line.prev('.field-collection-line');
                var next_line = line.next('.field-collection-line');

                line.remove();
                update_move_buttons(next_line, previous_line);

                var lines = container.find('.field-collection-line');

                if (!lines.length) {
                    var empty_message = field.find('.field-collection-empty');
                    var header_message = field.children('.field-collection-header');
                    var actions = field.children('.multi-actions');
                    var remove_button = actions.children('.field-collection-remove-line');

                    empty_message.slideDown();
                    header_message.slideUp();
                    remove_button.fadeOut();
                };
            });
            return false;
        });

        // Bind the up button
        $('form.zeam-form button.field-collection-move-up').live('click', function () {
            var button = $(this);
            var line = button.closest('.field-collection-line');
            var previous_line = line.prev();

            if (previous_line.is('.field-collection-line')) {
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
        $('form.zeam-form button.field-collection-move-down').live('click', function () {
            var button = $(this);
            var line = button.closest('.field-collection-line');
            var next_line = line.next();

            if (next_line.is('.field-collection-line')) {
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
})(jQuery);
