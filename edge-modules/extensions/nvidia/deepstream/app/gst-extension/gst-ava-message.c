#include "gst-ava-message.h"

#include "stdio.h"
#include "stdlib.h"
#include "string.h"



void gst_ava_message_init(GstAVAMessage *gst_ava_message)
{
    gst_ava_message->sequence_number = 0;    
    gst_ava_message->timestamp = 0;
}

GstAVAMessage* gst_ava_message_empty_message()
{
    static GstAVAMessage message;
    gst_ava_message_init(&message);
    return &message;
}   

GType gst_ava_message_api_get_type(void)
{
    static const gchar *tags[] = { gst_ava_MESSAGE_META_TAG, NULL };
    static volatile GType type;

    if (g_once_init_enter (&type)) {
        GType _type = gst_meta_api_type_register(gst_ava_MESSAGE_META_API_NAME, tags);
        g_once_init_leave(&type, _type);
    }
    return type;
}

static gboolean gst_ava_message_meta_init(GstMeta *meta, gpointer params, GstBuffer *buffer)
{
    GstAVAMessageMeta *gst_ava_meta = (GstAVAMessageMeta *)meta;     
    gst_ava_message_init(&(gst_ava_meta->message));
    
    return TRUE;
}



static void gst_ava_message_meta_free(GstMeta *meta, GstBuffer *buffer)
{
    

}

// Add message to the buffer
GstAVAMessageMeta* gst_ava_buffer_add_message( GstBuffer *buffer, GstAVAMessage *gstavaMsg)
{   
    const GstMetaInfo *meta_info = gst_ava_message_meta_get_info(); 
    GstAVAMessageMeta *gstavameta = (GstAVAMessageMeta *)gst_buffer_add_meta(buffer, meta_info, NULL);   

    gstavameta->message.sequence_number = gstavaMsg->sequence_number;     
    gstavameta->message.timestamp = gstavaMsg->timestamp;

    return gstavameta;
}

static gboolean gst_ava_message_meta_transform(GstBuffer *dest_buf, GstMeta *src_meta, GstBuffer *src_buf, GQuark type, gpointer data)
{
    
    GstAVAMessageMeta *gst_ava_srcmeta = (GstAVAMessageMeta *)src_meta;
    GstAVAMessageMeta *gst_ava_destmeta = gst_ava_buffer_add_message(dest_buf, &(gst_ava_srcmeta->message));
    
    return TRUE;
}

const GstMetaInfo *gst_ava_message_meta_get_info(void)
{
    static const GstMetaInfo *metainfo = NULL;
 
    if (g_once_init_enter (&metainfo)) {

        const GstMetaInfo *meta = gst_meta_register (gst_ava_message_api_get_type(), 
                                                     gst_ava_MESSAGE_META_IMPL_NAME,           
                                                     sizeof (GstAVAMessageMeta),    
                                                     (GstMetaInitFunction)gst_ava_message_meta_init,
                                                     (GstMetaFreeFunction) gst_ava_message_meta_free,
                                                     (GstMetaTransformFunction)gst_ava_message_meta_transform);
        g_once_init_leave (&metainfo, meta);
    }
    return metainfo;
}

// Gets message from the buffer
GstAVAMessage *gst_ava_buffer_get_message(GstBuffer *buffer)
{
    GstAVAMessageMeta *gstavameta = (GstAVAMessageMeta *)gst_buffer_get_meta((buffer), gst_ava_MESSAGE_META_TYPE);
    
    if (gstavameta == NULL)
        return gst_ava_message_empty_message();
    else
        return &(gstavameta->message);       
}


// Removes message from buffer
gboolean gst_ava_buffer_remove_message(GstBuffer *buffer)
{   
    GstAVAMessageMeta *gstavameta = (GstAVAMessageMeta *)gst_buffer_get_meta((buffer), gst_ava_MESSAGE_META_TYPE);

    if (gstavameta == NULL)
        return TRUE;
    
    if ( !gst_buffer_is_writable(buffer))
        return FALSE;
    
    return gst_buffer_remove_meta(buffer, &(gstavameta->gstMeta));
}