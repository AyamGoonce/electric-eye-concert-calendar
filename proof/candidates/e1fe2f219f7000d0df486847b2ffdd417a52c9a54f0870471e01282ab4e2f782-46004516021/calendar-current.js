(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e1fe2f219f7000d0.js","sha256":"e1fe2f219f7000d0df486847b2ffdd417a52c9a54f0870471e01282ab4e2f782","count":2118,"publishedAt":"2026-11-27T13:11:16Z","state":"calendar-state.json","stateSha256":"16fedbee47864ec4d40e9f659ce2ce5221a55f3f40ea5a980e1c027dff315537","sourceState":"calendar-source-state.json","sourceStateSha256":"f9ed3c579c0f4f296b892ff6b5a9b0c0e0f8338d97e94b9852238652932dc906"});
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
