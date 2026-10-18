(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b807224a634234a9.js","sha256":"b807224a634234a91993a73d35865370a1b6de081cf57a31231b02d2a1232d5c","count":2070,"publishedAt":"2026-10-18T11:19:07Z","state":"calendar-state.json","stateSha256":"d099b540da5709720c834dd761c0c71d2addcb3b25b053b89b349e1d801c1b3d","sourceState":"calendar-source-state.json","sourceStateSha256":"c17f4a8c237e915cbbc51fbe97aad0ac6c64871ea6fa371ab20688b17ab87007"});
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
