
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


    $(document).ready(function (){
        $('form.zeam-form div.field-list').each(function (){
            var field = $(this);
            var counter = field.find('input.field-list-counter');
            var base = field.find('div.field-list-template');
            var template = new jsontemplate.Template(base.get(0).innerHTML, {});

            // Remove the template from the DOM.
            base.html('');

            // Bind the add button
            field.find('input.field-list-add-line').bind('click', function() {
                var identifier = counter.val();
                var html = $(template.expand({identifier: identifier}));

                html.insertBefore(base);
                counter.val(increment(identifier));
                return false;
            });

            // Bind the remove button
            field.find('input.field-list-remove-line').bind('click', function() {
                field.find('input.field-list-line-selector:checked').each(function (){
                    var selector = $(this);

                    selector.parent().remove();
                });
                return false;
            });

            // Bind the up button
            field.find('button.field-list-move-up').live('click', function () {
                var button = $(this);
                var line = button.parent();
                var previous_line = line.prev();

                if (previous_line.hasClass('field-list-line')) {
                    var name_info = field_name_regexp.exec(line.attr('rel'));
                    var base_name = name_info[1];
                    var count = name_info[2];

                    var previous_name_info = field_name_regexp.exec(previous_line.attr('rel'));
                    var previous_count = previous_name_info[2];

                    update_line_names(line, base_name, previous_count);
                    update_line_names(previous_line, base_name, count);

                    line.remove();
                    line.insertBefore(previous_line);
                };
                return false;
            });

            // Bind the down button
            field.find('button.field-list-move-down').live('click', function () {
                var button = $(this);
                var line = button.parent();
                var next_line = line.next();

                if (next_line.hasClass('field-list-line')) {
                    var name_info = field_name_regexp.exec(line.attr('rel'));
                    var base_name = name_info[1];
                    var count = name_info[2];

                    var next_name_info = field_name_regexp.exec(next_line.attr('rel'));
                    var next_count = next_name_info[2];

                    update_line_names(line, base_name, next_count);
                    update_line_names(next_line, base_name, count);

                    line.remove();
                    line.insertAfter(next_line);
                };
                return false;
            });
        });
    });
})(jQuery);
