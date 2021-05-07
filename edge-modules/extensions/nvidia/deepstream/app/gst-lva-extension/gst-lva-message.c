#include "gst-lva-message.h"

#include "stdio.h"
#include "stdlib.h"
#include "string.h"



void gst_lva_message_init(GstLVAMessage *gst_lva_message)
{
    gst_lva_message->sequence_number = 0;    
    gst_lva_message->timestamp = 0;
}

GstLVAMessage* gst_lva_message_empty_message()
{
    static GstLVAMessage message;
    gst_lva_message_init(&message);
    return &message;
}   

GType gst_lva_message_api_get_type(void)
{
    static const gchar *tags[] = { GST_LVA_MESSAGE_META_TAG, NULL };
    static volatile GType type;

    if (g_once_init_enter (&type)) {
        GType _type = gst_meta_api_type_register(GST_LVA_MESSAGE_META_API_NAME, tags);
        g_once_init_leave(&type, _type);
    }
    return type;
}

static gboolean gst_lva_message_meta_init(GstMeta *meta, gpointer params, GstBuffer *buffer)
{
    GstLVAMessageMeta *gst_lva_meta = (GstLVAMessageMeta *)meta;     
    gst_lva_message_init(&(gst_lva_meta->message));
    
    return TRUE;
}



static void gst_lva_message_meta_free(GstMeta *meta, GstBuffer *buffer)
{
    

}

// Add message to the buffer
GstLVAMessageMeta* gst_lva_buffer_add_message( GstBuffer *buffer, GstLVAMessage *gstlvaMsg)
{   
    const GstMetaInfo *meta_info = gst_lva_message_meta_get_info(); 
    GstLVAMessageMeta *gstlvameta = (GstLVAMessageMeta *)gst_buffer_add_meta(buffer, meta_info, NULL);   

    gstlvameta->message.sequence_number = gstlvaMsg->sequence_number;     
    gstlvameta->message.timestamp = gstlvaMsg->timestamp;

    return gstlvameta;
}

static gboolean gst_lva_message_meta_transform(GstBuffer *dest_buf, GstMeta *src_meta, GstBuffer *src_buf, GQuark type, gpointer data)
{
    
    GstLVAMessageMeta *gst_lva_srcmeta = (GstLVAMessageMeta *)src_meta;
    GstLVAMessageMeta *gst_lva_destmeta = gst_lva_buffer_add_message(dest_buf, &(gst_lva_srcmeta->message));
    
    return TRUE;
}

const GstMetaInfo *gst_lva_message_meta_get_info(void)
{
    static const GstMetaInfo *metainfo = NULL;
 
    if (g_once_init_enter (&metainfo)) {

        const GstMetaInfo *meta = gst_meta_register (gst_lva_message_api_get_type(), 
                                                     GST_LVA_MESSAGE_META_IMPL_NAME,           
                                                     sizeof (GstLVAMessageMeta),    
                                                     (GstMetaInitFunction)gst_lva_message_meta_init,
                                                     (GstMetaFreeFunction) gst_lva_message_meta_free,
                                                     (GstMetaTransformFunction)gst_lva_message_meta_transform);
        g_once_init_leave (&metainfo, meta);
    }
    return metainfo;
}

// Gets message from the buffer
GstLVAMessage *gst_lva_buffer_get_message(GstBuffer *buffer)
{
    GstLVAMessageMeta *gstlvameta = (GstLVAMessageMeta *)gst_buffer_get_meta((buffer), GST_LVA_MESSAGE_META_TYPE);
    
    if (gstlvameta == NULL)
        return gst_lva_message_empty_message();
    else
        return &(gstlvameta->message);       
}


// Removes message from buffer
gboolean gst_lva_buffer_remove_message(GstBuffer *buffer)
{   
    GstLVAMessageMeta *gstlvameta = (GstLVAMessageMeta *)gst_buffer_get_meta((buffer), GST_LVA_MESSAGE_META_TYPE);

    if (gstlvameta == NULL)
        return TRUE;
    
    if ( !gst_buffer_is_writable(buffer))
        return FALSE;
    
    return gst_buffer_remove_meta(buffer, &(gstlvameta->gstMeta));
}