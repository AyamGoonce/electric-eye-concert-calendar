(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.291d5940289abc62.js","sha256":"291d5940289abc6281ea5a9edebde71a4f00b17c4935a26239e562db782cfe1a","count":2529,"publishedAt":"2026-09-05T15:25:57Z","state":"calendar-state.json","stateSha256":"24bd0f9fba5b1471776b9812f70402ae231ac036757d83b820b7f81bd055ce6a"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
