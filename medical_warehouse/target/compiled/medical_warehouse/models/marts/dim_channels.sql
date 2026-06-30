with staging as (
    select * from "medical_db"."analytics"."stg_telegram_messages"
)

select
    md5(channel_name) as channel_key,
    channel_name,
    case 
        when channel_name ilike '%pharma%' then 'Pharmaceutical'
        when channel_name ilike '%cosmetics%' then 'Cosmetics'
        else 'Medical'
    end as channel_type,
    min(message_date) as first_post_date,
    max(message_date) as last_post_date,
    count(message_id) as total_posts,
    coalesce(avg(view_count), 0) as avg_views
from staging
group by channel_name