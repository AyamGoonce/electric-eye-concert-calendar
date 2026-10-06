(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3681630db811fe73.js","sha256":"3681630db811fe737c723db68079dedf9ad6fef92d419f39bab3c0a43e68b5fa","count":2214,"publishedAt":"2026-10-06T17:16:10Z","state":"calendar-state.json","stateSha256":"307a611e43e32f5ba35718cecdcfa46de895373b0af08beb1daf8506d2341c9c","sourceState":"calendar-source-state.json","sourceStateSha256":"bab9a83444067043d524c05bb4a6e7e68ac554c14c03acc11a6923286b346f16"});
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
