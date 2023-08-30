-- NGINX Lua handler
local function waf_handler()
    local req_headers = ngx.req.get_headers()
    local query = req_headers["query"]  -- Adjust to your header field

    if query then
        local res = ngx.location.capture("/verify", {
            method = ngx.HTTP_POST,
            args = { query = query }
        })

        if res.status == 200 and res.body == "ALLOW" then
            -- Process the query and return the appropriate response
            -- Replace this with your application logic
            ngx.say("Query processed successfully.")
        else
            ngx.exit(ngx.HTTP_FORBIDDEN)
        end
    end
end

waf_handler()
