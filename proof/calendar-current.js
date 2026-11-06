(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ef8a4f11692c849c.js","sha256":"ef8a4f11692c849cc8126c972fffecf3ba7a24d1730ac97d0692800f1075bbe3","count":2040,"publishedAt":"2026-11-06T23:15:35Z","state":"calendar-state.json","stateSha256":"84f0ecdbb7cf39623d61aadb5f23bcee838a058023e06322f6328c1364c76d11","sourceState":"calendar-source-state.json","sourceStateSha256":"bc0e13c6f78ab81772bee85e5752d6ccfd2ca03579edffad3f6dd558c415ab3d"});
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
