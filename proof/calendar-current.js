(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5705814830d1d869.js","sha256":"5705814830d1d8696f57cae25296dc5cbe8f4827d293a3c60a31f7586adfd76f","count":2011,"publishedAt":"2026-11-07T13:15:29Z","state":"calendar-state.json","stateSha256":"957918d75555d8708e2226c8aef6873a837a2691aee453153e03de19bd0204e5","sourceState":"calendar-source-state.json","sourceStateSha256":"de80629f4a5579b1fdfa84e35535ef140f940b561774c097dfe368397e118322"});
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
