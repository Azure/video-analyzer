![ava_widgets_banner_github.png](https://user-images.githubusercontent.com/51399662/119260323-fc97bf00-bbda-11eb-82d0-c31fa64b8e38.png)

# Azure Video Analyzer widgets

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/%3C%2F%3E-TypeScript-%230074c1.svg)](https://www.typescriptlang.org/)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-f8bc45.svg)](https://github.com/prettier/prettier)

This repo conatins the Azure Video Analyzer widgets and web component packages. Below you can find documentation and examples on how to use these pieces.

## Introduction

[Video Analyzer](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/overview) provides a platform to build intelligent video applications that span the edge and the cloud. It offers the capability to capture, record, and analyze live video along with publishing the results - video and/or video analytics.

The material in this repository is designed to help in building applications on the Video Analyzer platform. Below you'll find sections on:

-   Installing the Video Analyzer widget library
-   Player widget

We also have a how-to in our document site on [using the Video Analyzer player widget](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/player-widget).

## Installing Video Analyzer library

The widgets are distributed as an NPM package. There are a couple ways to install the library.

-   **Command line** - For consuming the NPM package directly, you can install it using the npm command.
    ```
    npm install @azure/video-analyzer-widgets
    ```
-   **Javascript HTML object** - You can import the latest version of the widget directly into your HTML file by using this script segment.

    ```html
            ...
            <!-- Add Video Analyzer player web component -->
            <script async type="module" src="https://unpkg.com/@azure/video-analyzer-widgets"></script>
        </body>
    </html>
    ```

-   **Window object** - If you want expose the widget code on the window, you can import the latest version by using this script segment.
    ```html
            ...
            <!-- Add Video Analyzer player web component -->
            <script async src="https://unpkg.com/@azure/video-analyzer-widgets@latest/dist/global.min.js"></script>
        </body>
    </html>
    ```

## Player widget

The player widget can be used to play back video that has been stored in the Video Analyzer service. The section below details:

-   How to add a player widget to your application
-   Properties, events, and methods
-   Samples showing use of the widget

### Creating a player widget

Player widget is a web-component that can be created in your base HTML code, or dynamically at run time.

-   Creating using HTML
    ```html
      <body>
    	<ava-player width="920px"><ava-player>
      </body>
    ```
-   Creating dynamically using window
    ```typescript
    const avaPlayer = new window.ava.widgets.player();
    document.firstElementChild.appendChild(avaPlayer);
    ```
-   Creating dynamically with Typescript

    ```typescript
    import { Player } from '@azure/video-analyzer-widgets';

    const avaPlayer = new Player();
    document.firstElementChild.appendChild(avaPlayer);
    ```

### Properties, events and methods

The player has a series of properties as defined in the below table. Configuration is required to get the player to run initially.

| Name   | Type             | Default | Description                        |
| ------ | ---------------- | ------- | ---------------------------------- |
| width  | string           | 100%    | Reflects the value of widget width |
| config | IAvaPlayerConfig | null    | Widget configuration               |

There are also a couple of events that fire under various conditions. None of the events have parameters associated with them. It is important to deal with the TOKEN_EXPIRED event so that playback doesn't stop.

| Name          | Parameters | Description                                       |
| ------------- | ---------- | ------------------------------------------------- |
| TOKEN_EXPIRED | -          | Callback to invoke when AVA JWT token is expired. |
| PLAYER_ERROR  | -          | Callback to invoke there is an error.             |

The player has a few methods you can use in your code. These can be useful for building your own controls.

| Name           | Parameters                      | Description                                                                                              |
| -------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------- |
| constructor    | config: IAvaPlayerConfig = null | Widget constructor. If called with config, you don’t need to call _configure_ function                   |
| setAccessToken | jwtToken:string                 | Update the widget token.                                                                                 |
| configure      | config: IAvaPlayerConfig        | Update widget configuration.                                                                             |
| load           | -                               | Loads and initialize the widget according to provided configuration. If not called, widget will be empty |
| play           | -                               | Play the player                                                                                          |
| pause          | -                               | Pause the player                                                                                         |

### Code samples

There are a few code samples below detailing basic usage, how to dynamically create the widget during run time, how to deal with refreshing the token, and use in an Angular application.

#### Basic usage

This code shows how to create the player widget as an HTML tag, then configure the widget, and load the data to make it start playing using Javacript.

```html
<script>
    function onAVALoad() {
        // Get player instance
        const avaPlayer = document.querySelector('ava-player');

        // Configure widget with AVA API configuration
        avaPlayer.configure({
            token: '<AVA-API-JWT-TOKEN>',
            clientApiEndpointUrl: '<CLIENT-ENDPOINT-URL>',
            videoName: '<VIDEO-NAME-FROM-AVA-ACCOUNT>'
        });

        avaPlayer.load();
    }
</script>
<script async type="module" src="https://unpkg.com/@azure/video-analyzer-widgets" onload="onAVALoad()"></script>
<body>
    <ava-player></ava-player>
</body>
```

#### Dynamically creating the widget

This code shows how to create a widget dynamically with Javascript code without using the separate configure function. It adds the widget to a premade div container.

```html
<script>
    function onAVALoad() {
        // Get widget container
        const widgetContainer = document.querySelector('#widget-container');

        // Create new player widget
        const playerWidget = new window.ava.widgets.player({
            token: '<AVA-API-JWT-TOKEN>',
            clientApiEndpointUrl: '<CLIENT-ENDPOINT-URL>',
            videoName: '<VIDEO-NAME-FROM-AVA-ACCOUNT>'
        });

        widgetContainer.appendChild(playerWidget);

        // Load the widget
        playerWidget.load();
    }
</script>
<script async src="https://unpkg.com/@azure/video-analyzer-widgets@latest/dist/global.min.js" onload="onAVALoad()"></script>
<body>
    <div id="widget-container"></div>
</body>
```

#### Token refresh

This section shows create a widget with native JS code, configure the widget, and load the data. It adds in an event listener so that when the token is expired, it will update the token. You will of course need to provide your own code to generate a new token based on the method you used.

```html
<script>
    function onAVALoad() {
        // Get player instance
        const avaPlayer = document.querySelector("ava-player");

        // Adding token expired listener
        avaPlayer.addEventListener('TOKEN_EXPIRED', async () => {
            const token = await fetch(‘<request-to-generate-token>’);
            avaPlayer.setAccessToken(token);
        });

        // Configure widget with AVA API configuration
        avaPlayer.configure({
            token: '<AVA-API-JWT-TOKEN>',
            clientApiEndpointUrl: '<CLIENT-ENDPOINT-URL>',
            videoName: '<VIDEO-NAME-FROM-AVA-ACCOUNT>'
        });

        // Load the widget
        avaPlayer.load();
    }
</script>
<script async type="module" src="https://unpkg.com/@azure/video-analyzer-widgets" onload="onAVALoad()"></script>
<body>
    <ava-player width="920px"></ava-player>
</body>
```

#### Player widget in an Angular application

To use the player widget in an Angular application, you'll need to follow the steps below.

1. Go to your _src/main.ts_ file and add the following code:

    ```typescript
    import { Player } from '@azure/video-analyzer-widgets';

    /*
     * Ensure that tree-shaking doesn't remove this component from * the bundle.
     * There are multiple ways to prevent tree shaking, of which this * is one.
     */
    Player;
    ```

1. To allow an NgModule to contain Non-Angular element names, add the following code in your application module Typescript file _app.module.ts_:

    ```typescript
        import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';

        @NgModule({
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        });
    ```

1. Now you can start using widget. Replace the HTML template in your app.component.html, file with the following markup:
    ```html
    <template>
        <ava-player width="920px"></ava-player>
    </template>
    ```
    Alternatively, you can create a new instance of the widget using Typescript, and add it to the DOM.
