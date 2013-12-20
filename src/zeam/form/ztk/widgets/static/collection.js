
// Requires: json-template.js and jQuery 1.7

(function ($, jsontemplate){
    var FIELD_NAME_REGEXP = /(.*)\.field\.(\d+)$/;

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

    var create_template = function($node) {
        if (!$node.length) {
            // allowAdding is false;
            return undefined;
        };

        var identifier = $node.attr('rel'),
            template = new jsontemplate.Template(
                $.trim($node.get(0).innerHTML), {
                    // For the moment this use an hijack version of
                    // json-template.
                    undefined_callable: function(name){
                        return '{' + name + '}';
                    }
                });

        // Remove the template from the DOM.
        $node.remove();
        // Return an object that let you render the template
        return {
            identifier: identifier,
            template: template,
            render: function(identifier) {
                var parameters = {};
                parameters[this.identifier] = identifier;

                var data = $(this.template.expand(parameters));
                if (!data.is('.field-collection-line')) {
                    data = data.find('.field-collection-line:first');
                };

                // The line might contains other field-collection
                data.find('div.field-collection').each(function (){
                    create_field($(this));
                });

                return data;
            }
        };
    };

    var update_line_names = function($line, base_name, count) {
        var selector_name = base_name + '.checked.',
            present_name = base_name + '.present.',
            field_name = base_name + '.field.';

        var rewriter = function () {
            var $input = $(this),
                input_name,
                template_name = $input.attr('name');

            if (starts_with(template_name, selector_name)) {
                $input.attr('name', selector_name + count);
            } else if (starts_with(template_name, present_name)) {
                $input.attr('name', present_name + count);
            } else if (starts_with(template_name, field_name)) {
                input_name = field_name + count;
                var i = field_name.length;

                // Consume the old count
                for (; i < template_name.length && template_name[i] != '.'; i++);
                // Copy the end of the old name to the new one
                for (; i < template_name.length; i++) {
                    input_name += template_name[i];
                };
                $input.attr('name', input_name);
            };
        };
        // Rewrite name for input, textarea and select tags.
        $line.find('input').each(rewriter);
        $line.find('textarea').each(rewriter);
        $line.find('select').each(rewriter);

        // Update the rel attribute on the file.
        $line.attr('rel', field_name + count);
    };

    var update_move_buttons = function($line_top, $line_bottom) {
        // Show or hide move up/down button depending if it is the
        // first line or last line or not. This code exist because IE
        // 7 doesn't support last-child in CSS.
        if ($line_top.is(':first-child')) {
            $line_bottom.children('.ordering-actions').children(
                '.field-collection-move-up').show();
            $line_top.children('.ordering-actions').children(
                '.field-collection-move-up').hide();
        };
        if ($line_bottom.is(':last-child')) {
            $line_top.children('.ordering-actions').children(
                '.field-collection-move-down').show();
            $line_bottom.children('.ordering-actions').children(
                '.field-collection-move-down').hide();
        };
    };

    var create_field = function($field) {
        if (!$field.is('.field-collection')) {
            return;
        };

        var $container = $field.find('.field-collection-lines:first'),
            template = create_template($field.children('.field-collection-template'));


        var move_line_down = function () {
            var $line = $(this).closest('.field-collection-line'),
                $next_line = $line.next();

            if ($next_line.is('.field-collection-line')) {
                var name_info = FIELD_NAME_REGEXP.exec($line.attr('rel')),
                    base_name = name_info[1],
                    count = name_info[2];

                var next_name_info = FIELD_NAME_REGEXP.exec($next_line.attr('rel')),
                    next_count = next_name_info[2];

                $line.remove();
                $line.insertAfter($next_line);
                update_line_names($line, base_name, next_count);
                update_line_names($next_line, base_name, count);
                update_move_buttons($next_line, $line);
            };
            return false;
        };

        var move_line_up = function () {
            var $line = $(this).closest('.field-collection-line'),
                $previous_line = $line.prev();

            if ($previous_line.is('.field-collection-line')) {
                var name_info = FIELD_NAME_REGEXP.exec($line.attr('rel')),
                    base_name = name_info[1],
                    count = name_info[2];

                var previous_name_info = FIELD_NAME_REGEXP.exec(
                    $previous_line.attr('rel')),
                    previous_count = previous_name_info[2];

                $line.remove();
                $line.insertBefore($previous_line);
                update_line_names($line, base_name, previous_count);
                update_line_names($previous_line, base_name, count);
                update_move_buttons($line, $previous_line);
            };
            return false;
        };

        var remove_line =  function() {
            var $selected = $container.children(
                '.field-collection-line').children(
                    '.line-actions').children(
                        'input.field-collection-line-selector:checked');

            $selected.each(function (){
                var $line = $(this).closest('.field-collection-line'),
                    $previous_line = $line.prev('.field-collection-line'),
                    $next_line = $line.next('.field-collection-line');

                $line.remove();
                update_move_buttons($next_line, $previous_line);

                var $lines = $container.find('.field-collection-line');

                if (!$lines.length) {
                    var $empty_message = $field.find('.field-collection-empty'),
                        $header_message = $field.children('.field-collection-header'),
                        $actions = $field.children('.multi-actions'),
                        $remove_button = $actions.children('.field-collection-remove-line');

                    $empty_message.slideDown();
                    $header_message.slideUp();
                    $remove_button.fadeOut();
                };
            });
            return false;
        };

        var add_line = function() {
            // Clear the empty message
            var $header_message = $field.children('.field-collection-header'),
                $empty_message = $field.children('.field-collection-empty');

            if ($empty_message.is(':visible')) {
                $header_message.slideDown();
                $empty_message.slideUp();
            };

            // Display the remove button
            var $actions = $field.children('.multi-actions'),
                $remove_button = $actions.children('.field-collection-remove-line');
            if (!$remove_button.is(':visible')) {
                $remove_button.fadeIn();
            };

            // Add a line
            var $counter = $field.children('input.field-collection-counter'),
                identifier = $counter.val(),
                $new_line = template.render(identifier),
                $container = $field.find('.field-collection-lines:first'),
                $previous_line = $container.children('.field-collection-line:last');

            if (!$previous_line.length) {
                $previous_line = $new_line;
            };
            $new_line.appendTo($container);
            update_move_buttons($previous_line, $new_line);
            $counter.val(increment(identifier));
            $new_line.trigger('addline-zeamform');
            return false;
        };

        // Bind events
        $field.on('click', 'input.field-collection-add-line', add_line);
        $field.on('click', 'input.field-collection-remove-line', remove_line);
        $field.on('click', 'button.field-collection-move-up', move_line_up);
        $field.on('click', 'button.field-collection-move-down', move_line_down);

        // Clear style on any existing buttons.
        update_move_buttons(
            $container.children('.field-collection-line:first'),
            $container.children('.field-collection-line:last'));
    };

    $.extend($.fn, {
        ZeamCollectionWidget: function () {
            return $(this).each(function() { create_field($(this));});
        }
    });

    $(document).ready(function (){
        // Load existing fields.
        $('form div.field-collection').ZeamCollectionWidget();
    });
})(jQuery, jsontemplate);
