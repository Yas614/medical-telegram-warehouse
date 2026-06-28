with raw_source as (
    select * from {{ source('raw_data', 'telegram_messages') }}
)

select
    message_id,
    replace(channel_name, '@', '') as channel_name,
    cast(message_date as timestamp) as message_date,
    coalesce(message_text, '') as message_text,
    length(coalesce(message_text, '')) as message_length,
    coalesce(has_media, false) as has_image,
    image_path,
    coalesce(views, 0) as view_count,
    coalesce(forwards, 0) as forward_count
from raw_source
where message_id is not null